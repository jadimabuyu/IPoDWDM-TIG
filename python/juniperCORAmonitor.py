from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from threading import Timer
import re, ast, time, os, docker, time, logging, logging.config

dockerAPI = docker.DockerClient(base_url='unix://var/run/docker.sock')
instanceIndex=int(dockerAPI.containers.list(filters={'id':os.environ["HOSTNAME"]})[0].labels['com.docker.compose.container-number'])-1

host= ast.literal_eval(os.environ["hosts"])[instanceIndex]

INFLUXDB_TOKEN=os.environ['INFLUXDB_TOKEN']
INFLUXDB_URL='http://influxdb:8086'
INFLUXDB_ORG=os.environ['INFLUXDB_ORG']
INFLUXDB_BUCKET=os.environ['INFLUXDB_BUCKET']
INFLUXDB_USERNAME=os.environ['INFLUXDB_USERNAME']
INFLUXDB_PASSWORD=os.environ['INFLUXDB_PASSWORD']

junosDev = Device(host=host['host'], user=host['user'], passwd=host['passwd']).open()

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def portIdentifier(interface):
	reg=re.match(r'et-(\d)/(\d)/(\d+)',interface)
	return str(reg[1]),str(reg[2]),str(reg[3])

def junosGetPM(interface):		
    intpm= junosDev.rpc.get_interface_transport_pm_optics_c_information(normalize=True,interface_name=interface)
    pmNames=intpm.findall(f'interface-information/physical-interface/transport-interval-information/transport-interval/transport-optics-cur/transport-optics-cur-name')
    pm={x.text:'' for x in pmNames}
    for x in pm.keys():
        pm[x]=intpm.find(f'interface-information/physical-interface/transport-interval-information/transport-interval/transport-optics-cur/[transport-optics-cur-name="{x}"]/transport-optics-cur-cur').text
    return pm
		
def junosGetInterfaceInfo(interface):
    intInfo=junosDev.rpc.get_interface_information(normalize=True,interface_name=interface)
    opticsApps=junosDev.rpc.get_interface_optics_applications_diagnostics(normalize=True,interface_name=interface)
    media_code_desc=""
    try:
        operStatus=intInfo.find(f'physical-interface/oper-status').text
        speed = ""
        try:
            speed=opticsApps.find(f'physical-interface/optics-applications/current-speed').text + 'E'
        except:
            speed=intInfo.find(f'physical-interface/speed').text

        media_code_desc=intInfo.find(f'physical-interface/optics-properties/media-code-desc').text
        freq=intInfo.find(f'physical-interface/optics-properties/frequency').text
        ibps=intInfo.find(f'physical-interface/traffic-statistics/input-bps').text
        obps=intInfo.find(f'physical-interface/traffic-statistics/output-bps').text
        uncorrectedWords=intInfo.find(f'physical-interface/optic-fec-statistics/fec-uncorrected-words').text
    except:
        pass
    return {"operStatus":operStatus,"waveorfreq":freq,"ibps":ibps,"obps":obps,"uncorrectedWords":uncorrectedWords,"media-code-desc":media_code_desc,"speed":speed}

def junosGetModuleInfo(interface):
	fpc,pic,port=portIdentifier(interface)	
	picDetail=junosDev.rpc.get_pic_detail(normalize=True,fpc_slot=fpc,pic_slot=pic)
	moduleVendor=picDetail.find(f'fpc/pic-detail/port-information/port/[port-number="{port}"]/sfp-vendor-name').text
	modulePN=picDetail.find(f'fpc/pic-detail/port-information/port/[port-number="{port}"]/sfp-vendor-pno').text
	chassisHardware=junosDev.rpc.get_chassis_inventory(normalize=True,)
	moduleSN=chassisHardware.find(f'chassis/chassis-module/[name="FPC {fpc}"]/chassis-sub-module/[name="PIC {pic}"]/chassis-sub-sub-module/[name="Xcvr {port}"]/serial-number').text
	description=chassisHardware.find(f'chassis/chassis-module/[name="FPC {fpc}"]/chassis-sub-module/[name="PIC {pic}"]/chassis-sub-sub-module/[name="Xcvr {port}"]/description').text
	return {"moduleVendor":moduleVendor,"modulePN":modulePN,"moduleSN":moduleSN,"description":description}


def getZRInt():
    intInfo=junosDev.rpc.get_interface_information(normalize=True)    
    zrInts=[x.getparent().getparent().find('name').text for x in intInfo.findall(f'physical-interface/optic-fec-mode/fec-mode') if 'FEC' in x.text]
    return zrInts

def main():
    interfaces=getZRInt()
    moduleInfo={}
    interfaceInfo={}
    pm={}
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for x in interfaces:
            sequence =[]
            pm[x]=junosGetPM(x)
            moduleInfo[x]=junosGetModuleInfo(x)
            interfaceInfo[x]=junosGetInterfaceInfo(x)
            for (j,k) in pm[x].items():
                 if k == ".":
                     continue
                 sequence.append(f"VDM,interface={x},host={host['host']} {str(re.sub(r' ', '_',j))}={float(k)}")
            for (j,k) in moduleInfo[x].items():
                sequence.append(f'VDM,interface={x},host={host["host"]} {j}="{str(k)}"')
            for (j,k) in interfaceInfo[x].items():
                if isinstance(k,int) or isinstance(k,float):
                    sequence.append(f"VDM,interface={x},host={host['host']} {j}={float(k)}")
                else:
                    sequence.append(f'VDM,interface={x},host={host["host"]} {j}="{k}"')
            write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, sequence)
            print(x)

#rt = RepeatedTimer(int(os.environ["poolInterval"]), main)

logging.basicConfig(
level=logging.INFO,
format="%(asctime)s [%(levelname)s] %(message)s",
handlers=[
    logging.StreamHandler()
]
)
logging.config.dictConfig({
'version': 1,
'disable_existing_loggers': True,
})

while 1:
    main()
    time.sleep(int(os.environ["poolInterval"]))
    
