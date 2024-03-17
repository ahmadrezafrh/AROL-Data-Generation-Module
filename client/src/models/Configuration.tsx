export default class Configuration {
    name: string
    machineriesSelected: MachinerySelected[]
  
    constructor(name: string = 'New configuration', MachineriesSelected: MachinerySelected[] = [], loaded: boolean = false) {
        this.name = name
        if (loaded) {
            this.machineriesSelected = MachineriesSelected.map(machinery => 
                new MachinerySelected(machinery.uid, machinery.modelName, machinery.sensorsSelected, machinery.faultFrequency, machinery.faultProbability, loaded)
            )
        } else {
            this.machineriesSelected = MachineriesSelected
        }
    }
     
    sortConfigurationMachineries(machinerySort : string): void {
        const updatedMachineriesSelected = [...this.machineriesSelected] 
        updatedMachineriesSelected.sort((a, b) => {
            switch (machinerySort) {
            case 'uid': {
                return a.uid > b.uid ? 1 : -1
            }
            case 'modelName': {
                return a.modelName > b.modelName ? 1 : -1
            }
            default: {
                console.error('Unknown sort term')
                return 0
            }
            }
        })
        this.machineriesSelected = updatedMachineriesSelected
    }

    setname(name: string): void {
        this.name = name
    }

    getname(): string {
        return this.name
    }

    getMachinery(uid: string) : MachinerySelected | null {
        const machinery = this.machineriesSelected.find((MachineriesSelected) => MachineriesSelected.uid === uid)
        return machinery || null 
    }

    setMachineryFaultFrequency(uid: string, faultFrequency: number): void {
        const machinery = this.getMachinery(uid)
        if (machinery) 
            machinery.setFaultFrequency(faultFrequency)
    }

    getMachineryFaultFrequency(uid: string ): number {
        const machinery = this.getMachinery(uid)
        if (machinery) 
            return machinery.getFaultFrequency()
        else 
            return 0
    }

    setMachineryFaultProbability(uid: string, faultProbability: number): void {
        const machinery = this.getMachinery(uid)
        if (machinery) 
            machinery.setFaultProbability(faultProbability)
    }

    getMachineryFaultProbability(uid: string ): number {
        const machinery = this.getMachinery(uid)
        if (machinery) 
            return machinery.getFaultProbability()
        else 
            return 0
    }
    
    addMachineriesSelected(uid: string, modelName: string): void {
        if (this.getname() == "New configuration") 
            this.setname('Unsaved configuration')
        const machinerySelected = new MachinerySelected(uid, modelName)
        this.machineriesSelected.push(machinerySelected)
    }
    
    removeMachineriesSelected(uid: string): void {
        this.machineriesSelected = this.machineriesSelected.filter((machinerySelected) => machinerySelected.uid !== uid)
    }

    addAllSensorConfToMachinery(uid: string, name: string, category: string, headsNum: number, dataFrequency: number): void {
        if (this.getname() == "New configuration") 
            this.setname('Unsaved configuration')
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const heads = Array.from({ length: headsNum }, (_, index) => index + 1)
            const sensor = machinery.getSensor(name)
            if (sensor){
                machinery.removeSensor(name)
                machinery.addSensor(name, category, heads, dataFrequency)
            }
            else{
                machinery.addSensor(name, category, heads, dataFrequency)
            }
        } 
        else
            console.error(`MachineriesSelected with uid ${uid} not found in the configuration.`)
    }

    addHeadSensorConfToMachinery(uid: string, name: string, category: string, head: number, dataFrequency: number): void {
        if (this.getname() == "New configuration") 
            this.setname('Unsaved configuration')
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor)
                sensor.addHead(head)
            else {
                const heads = [head]
                machinery.addSensor(name, category, heads, dataFrequency)
            }
        } 
        else
            console.error(`MachineriesSelected with uid ${uid} not found in the configuration.`)
    }

    removeAllSensorConfFromMachine(uid: string, name: string): void {
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor)
                machinery.removeSensor(name)
            else
                console.error(`Sensor ${name} not found in the configuration.`)
        } 
        else
            console.error(`Machinery with uid ${uid} not found in the configuration.`)
    }


    removeHeadSensorConfToMachinery(uid: string, name: string, head: number): void {
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor){
                if(sensor.getSensorHead(head)) {
                    sensor.removeHead(head)
                    if(sensor.getSensorNumHeads() === 0)
                        this.removeAllSensorConfFromMachine(uid, name)
                }
                else
                    console.error(`Head ${head} not present in sensor ${name}.`)
          } 
          else
            console.error(`Sensor ${name} not found in the configuration.`)
        } 
        else
            console.error(`Machinery with uid ${uid} not found in the configuration.`)
    }
      

    getSensorDataFrequency(uid: string, name: string): number {
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor) 
                return sensor.getSensorDataFrequency()
            else return 0
        }
        else return 0
    }

    setSensorDataFrequency(uid: string, name: string, datafrequency: number): void {
        if (this.getname() == "New configuration") 
            this.setname('Unsaved configuration')
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor) 
            sensor.setSensorDataFrequency(datafrequency)
        }
    }

    getSensorNumHeads(uid: string, name: string): number {
        const machinery = this.getMachinery(uid)
        if (machinery) {
            const sensor = machinery.getSensor(name)
            if (sensor) 
            return sensor.getSensorNumHeads()
            else return 0
        }
        else return 0
    }

    getHeadFromSensorFromMachinery(uid: string, name: string, head: number) : number | null {
        const machinery = this.getMachinery(uid)
        if (machinery){
            const sensor = machinery.getSensor(name)
            if (sensor){
                const hd = sensor.getSensorHead(head)
                if(hd)
                    return hd 
            }
        }
        return null
    }


}
  
    
class MachinerySelected {
    uid: string
    modelName: string
    sensorsSelected: SensorSelected[]
    faultFrequency: number
    faultProbability: number
    
    constructor(uid: string, modelName: string, SensorsSelected: SensorSelected[] = [], faultFrequency: number = 0, faultProbability: number = 0, loaded: boolean = false) {
        this.uid = uid
        this.modelName = modelName
        this.faultFrequency = faultFrequency
        this.faultProbability = faultProbability
        if (loaded) {
            this.sensorsSelected = SensorsSelected.map(sensor => new SensorSelected(sensor.name, sensor.category, sensor.heads, sensor.dataFrequency))
        } else {
            this.sensorsSelected = SensorsSelected
        }
    }
    
    addSensor(name: string, category: string, heads: number[], dataFrequency: number): void {
        const sensor= new SensorSelected(name, category, heads, dataFrequency)
        this.sensorsSelected.push(sensor)
    }

    removeSensor(name: string) : void{
        this.sensorsSelected = this.sensorsSelected.filter((SensorSelected) => SensorSelected.name !== name)
    }

    setFaultFrequency(faultFrequency: number) : void {
        this.faultFrequency = faultFrequency
    }

    setFaultProbability(faultProbability: number) : void {
        this.faultProbability = faultProbability
    }

    getFaultFrequency() : number {
        return this.faultFrequency
    }

    getFaultProbability() : number {
        return this.faultProbability 
    }

    getSensor(name: string): SensorSelected | null {
        const sensor = this.sensorsSelected.find(SensorSelected => SensorSelected.name === name)
        return sensor || null 
    }
}
  
    
class SensorSelected {
    name: string
    category: string
    heads: number[]
    dataFrequency: number

    constructor(name: string, category: string, heads: number[], dataFrequency: number) {
        this.name = name
        this.category = category
        this.heads = heads
        this.dataFrequency = dataFrequency
    }

    getSensorNumHeads() : number{
        return this.heads.length
    }

    getSensorHead(head : number) : number | null{
        return this.heads.find(h => h === head) || null
    }

    addHead(head : number) : void{
        this.heads.push(head)
    }

    removeHead(head : number) : void{
        this.heads = this.heads.filter(h => h != head)
    }

    setSensorDataFrequency(dataFrequency : number) : void{
        this.dataFrequency = dataFrequency
    }

    getSensorDataFrequency() : number{
        return this.dataFrequency
    }
}
    
    