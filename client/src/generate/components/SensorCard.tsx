import {
    Heading,
    Button,
    VStack,
    Divider,
    Text,
    HStack,
    Box,
    Tabs,
    Tab,
    TabPanels,
    TabPanel,
    Tooltip,
    Input,
    Grid,
    Spacer,
    GridItem
} from '@chakra-ui/react'
import {FiChevronDown, FiChevronUp, FiInfo} from 'react-icons/fi'
import {useEffect, useState, useContext} from 'react'
import Machinery from "../../models/Machinery"
import Sensor from '../../models/Sensor'
import sensorData from '../../database/sensor.json'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'
import Configuration from '../../models/Configuration'
import helperFunctions from '../../utils/HelperFunctions'

interface SensorsCardProps {
    machinery: Machinery
    isRunning: boolean
    isGenerable: boolean
    highlightTerm: string
}

export default function SensorCard(props: SensorsCardProps) {
    const {machinery, isRunning, isGenerable, highlightTerm} = props
    const [sensorsMap, setSensorsMap] = useState<Map<string, Sensor[]>>(new Map())
    const [sensors, setSensors] = useState<Sensor[]>([])
    const [isHovered, setIsHovered] = useState(false)
    const {configuration, setConfiguration, setIsSaved} = useContext(ConfigurationContext)
    const [isVisible, setIsVisible] = useState(false)

    // READ SENSORS FROM JSON
    useEffect(() => {
        const SensorArray: Sensor[] = []
        sensorData.forEach((element: any) => {
                const sensor = new Sensor(element)
                SensorArray.push(sensor)
            })
        
        setSensors(SensorArray)
      }, [])

    // SET ELEMENT VISIBLE FOR TRANSITION
    useEffect(() => {
        setIsVisible(true)
    }, [])

    // FROM SENSOR TO SENSOR MAP
    useEffect(() => {
        const map = new Map<string, Sensor[]>()
        sensors.forEach((el) => {
            if (map.has(el.category))
                map.get(el.category)?.push(el)
            else
                map.set(el.category, [el])
        })
        setSensorsMap(map)
    }, [sensors])

    // HANDLE FAULT FREQUENCY CHANGE
    const handleFaultFrequencyChange = (frequency : string) => {
        const regexp = /[a-zA-Z]/
        if (regexp.test(frequency) === true)
            return
        else {
            setIsSaved(false)
            setConfiguration((prevConfig) => {
                const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
                if (frequency !== '')
                    newConfig.setMachineryFaultFrequency(machinery.uid, parseInt(frequency))
                else
                    newConfig.setMachineryFaultFrequency(machinery.uid, 0)
                return newConfig
            })
        }
    }

    // HANDLE FAULT PROBABILITY CHANGE
    const handleFaultProbabilityChange = (probability : string) => {
        const regexp = /[a-zA-Z]/
        if (regexp.test(probability) === true || parseInt(probability) < 0 || parseInt(probability) > 100)
            return
        else {
            setIsSaved(false)
            setConfiguration((prevConfig) => {
                const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
                if (probability !== '')
                    newConfig.setMachineryFaultProbability(machinery.uid, parseInt(probability))
                else
                    newConfig.setMachineryFaultProbability(machinery.uid, 0)
                return newConfig
            })
        }
    }

    const getFaultFrequencyValue = () => {
        return configuration.getMachineryFaultFrequency(machinery.uid)
    }

    const getFaultProbabilityValue = () => {
        return configuration.getMachineryFaultProbability(machinery.uid)
    }


    return (
        <Box
        p={5}
        borderWidth={1}
        borderColor="gray.300"
        bgColor="white"
        rounded="md"
        textAlign="left"
        style={{
            transition: 'opacity 0.5s ease-in-out',
            opacity: isVisible ? 1 : 0,
          }}
        >
            <HStack alignItems="flex-start" pb={3}>
                <Heading
                    fontSize="md"
                    fontFamily="body"
                    fontWeight={550}
                    color="black"
                    whiteSpace="nowrap"  
                >
                {helperFunctions.highlightText(machinery.uid, 450, highlightTerm)} -
                </Heading>
                <Heading
                    fontSize="mg"
                    fontFamily="body"
                    fontWeight={450}
                    whiteSpace="nowrap"
                >
                {helperFunctions.highlightText(machinery.modelName, 450, highlightTerm)}
                </Heading>
            </HStack>
            <VStack>
                {sensorsMap.size > 0 &&
                    <>
                    <HStack>
                        <Text fontSize="md" fontWeight={600}>Select sensors</Text>
                        <Tooltip 
                            label={"To select the sensor, please enter the data generation frequency first"} 
                            isOpen={isHovered}
                            placement="top"
                        >
                        <Box
                            onMouseEnter={() => setIsHovered(true)}
                            onMouseLeave={() => setIsHovered(false)}
                        >
                        <FiInfo/>
                        </Box>
                        </Tooltip>
                    </HStack>
                    <Tabs variant='soft-rounded' colorScheme='green'  w ="full">
                        <HStack spacing={4} style={{ justifyContent: 'flex-start' }}>
                            {Array.from(sensorsMap.keys()).map((keyEntry, index) => (
                                <Tab key={`${keyEntry}-${index}`} w ="full">
                                    {keyEntry.toUpperCase()}
                                </Tab>
                            ))}
                        </HStack>
                        <TabPanels>
                            {Array.from(sensorsMap.entries()).map((mapKeyAndValue) => (
                            <Box key={`${mapKeyAndValue[0]}-${machinery.uid}`} overflowY="auto" maxH="260px">
                                <TabPanel key={mapKeyAndValue[0]}>
                                {   
                                    // If category contain sensors
                                    mapKeyAndValue[1].length > 0 &&
                                    mapKeyAndValue[1].map((sensor) => (
                                        <SensorEntry
                                            key={sensor.name}
                                            sensor={sensor}
                                            machinery={machinery}
                                            isRunning={isRunning}
                                            isGenerable={isGenerable}

                                        />   
                                    ))
                                }
                                {
                                // If category does NOT contain sensors
                                mapKeyAndValue[1].length === 0 &&
                                <Box
                                    w="full"
                                    textAlign="center"
                                    my="4"
                                >
                                    There are no sensors available in this category
                                </Box>
                                }
                                </TabPanel>
                            </Box>
                            ))
                            }
                        </TabPanels>
                    </Tabs>
                    <Grid
                        templateColumns="1fr 1fr 1fr 1fr"
                        templateRows="1fr"
                        w="full"
                        ml={7}
                    >
                        <GridItem colSpan={1} mt={1}>
                            <Text fontSize="sm" > Fault frequency </Text>
                        </GridItem>
                        <GridItem colSpan={1}>
                            <Input
                                w = "4.5vw"
                                type="number"
                                placeholder="ss"
                                size="sm"
                                fontSize="1vw"
                                onChange={(e) => handleFaultFrequencyChange(e.target.value)}
                                value={getFaultFrequencyValue() !== 0 ? getFaultFrequencyValue() : ''}
                            />
                        </GridItem>
                        <GridItem colSpan={1} mt={1}>
                            <Text fontSize="sm" > Fault probability </Text>
                        </GridItem>
                        <GridItem colSpan={1}>
                            <HStack>
                                <Input
                                    w = "4vw"
                                    type="number"
                                    placeholder="%"
                                    size="sm"
                                    fontSize="1vw"
                                    onChange={(e) => handleFaultProbabilityChange(e.target.value)}
                                    value={getFaultProbabilityValue() !== 0 ? getFaultProbabilityValue(): ''}
                                />
                                <Text fontSize="sm">%</Text>
                            </HStack>
                        </GridItem>
                    </Grid>
                    </>
                }
            </VStack>
        </Box>
    )
}


interface SensorEntryProps {
    sensor: Sensor
    machinery: Machinery
    isRunning: boolean
    isGenerable: boolean
}

function SensorEntry(props: SensorEntryProps) {

    const {sensor, machinery, isRunning, isGenerable} = props
    const [sensorExpanded, setSensorExpanded] = useState(false)
    const [allSensorsSelected, setAllSensorsSelected] = useState(false)
    const [sensorFrequency, setSensorFrequency] = useState(0)
    const {configuration, setConfiguration, setIsSaved} = useContext(ConfigurationContext)

    // CHECK IF ALL SENSORS OF THIS GROUP ARE SELECTED
    useEffect(() => {
        const numHeads = sensor.isHeadMounted ? machinery.numHeads : 1

        let numHeadsSelected = 0
        const mach = configuration.getMachinery(machinery.uid)
        if(mach){
            const machinerySensor = mach.getSensor(sensor.internalName)
            if (machinerySensor){
                numHeadsSelected = machinerySensor.getSensorNumHeads()
            }
        }
        setAllSensorsSelected(numHeadsSelected === numHeads)
    }, [configuration])


    useEffect(() => {
        const freq = getFrequencyValue()
        if (freq === 0)
            setSensorFrequency(0)
    }, [])


    // HANDLE SELECT ALL SENSORS 
    function handleSelectAllSensorsButtonClick() {
        const sensorHeads = sensor.isHeadMounted ? machinery.numHeads : 0
        let numHeads = sensorHeads
        if (sensorHeads === 0)
            numHeads = 1

        setIsSaved(false)
        setConfiguration((prevConfig) => {
            const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
            newConfig.addAllSensorConfToMachinery(machinery.uid, sensor.internalName, sensor.category, numHeads, sensorFrequency)
            return newConfig
        })
    }

    
    // HANDLE REMOVE ALL SENSORS 
    function handleRemoveAllSensorsButtonClick() {
        setIsSaved(false)
        setConfiguration((prevConfig) => {
            const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
            newConfig.removeAllSensorConfFromMachine(machinery.uid, sensor.internalName)
            return newConfig
        })
    }

    // GET SENSOR FREQUENCY VALUE
    function getFrequencyValue() {
        return configuration.getSensorDataFrequency(machinery.uid, sensor.internalName)
    }

    // GET BUTTON TEXT
    function getButtonText() {
        const nonHeadSensor = !sensor.isHeadMounted 
        if (isRunning && allSensorsSelected && isGenerable)
            return 'Generating'
        if (allSensorsSelected){
            if (nonHeadSensor)
                return 'Remove'

            return 'Remove All'
        }
        if (nonHeadSensor)
            return 'Select'

        return 'Select All'
    }

    // GET BUTTON COLOR - green/red
    function getButtonColor() {
        if (isRunning && allSensorsSelected && isGenerable)
            return 'black'

        if (allSensorsSelected)
            return 'red'

        return 'teal'
    }

    // HANDLE CHANGE SENSOR DATA FREQUENCY
    function handleSensorFrequencyChange(frequency: string) {
        const regexp = /[a-zA-Z]/
    
        let freq = 0
    
        if (regexp.test(frequency)) {
            return
        }
        if (frequency === '') {
            setSensorFrequency(0)
            freq = 0
        } else {
            const parsedFrequency = parseInt(frequency, 10)
            setSensorFrequency(parsedFrequency)
            freq = parsedFrequency
        }
        if (configuration.getSensorNumHeads(machinery.uid, sensor.internalName)) {
            setConfiguration((prevConfig) => {
                const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
                newConfig.setSensorDataFrequency(machinery.uid, sensor.internalName, freq)
                return newConfig
            })
        }
    }

    // HANDLE DISABLE SENSOR BUTTON
    function disableButton() {
        if(configuration.getSensorNumHeads(machinery.uid, sensor.internalName)){
            return false
        }
        else {
            if (sensorFrequency === 0 && getFrequencyValue() === 0) {
                return true
            }
            else{
                return false
            }
        }
    }


    return (
        <VStack
            w="full"
            justifyContent="left"
        >
        <Grid
            templateColumns="2fr 1fr 1fr"
            templateRows="1fr"
            w="full"
        >
            <GridItem colSpan={1}>
                <HStack>
                {sensor.isHeadMounted &&
                    <Box
                        _hover={{
                            cursor: 'pointer'
                        }}
                        onClick={() => {
                            setSensorExpanded((val) => (!val))
                        }}
                    >
                        {sensorExpanded ? <FiChevronUp/> : <FiChevronDown/>}
                    </Box>
                }
                <VStack alignItems="left">
                    <HStack justifyContent="space-between">
                        <Text fontSize="sm" mt={sensor.isHeadMounted ? "" : "1.5"}>{sensor.name}</Text>
                    </HStack>
                        {sensor.isHeadMounted &&
                            <Text fontSize="xs" color="gray.500" mt="0!important">{machinery.numHeads} heads</Text>
                        }
                </VStack>
                </HStack>
            </GridItem>
            <GridItem colSpan={1}>
                <Box>
                    <Input
                        w="4.5vw"
                        type="number"
                        mt={sensor.isHeadMounted ? "1.5" : ""}
                        placeholder={getFrequencyValue() === 0 ? "ss" : ""}
                        size="sm"
                        fontSize="1vw"
                        onChange={(e) => handleSensorFrequencyChange(e.target.value)}
                        value={sensorFrequency !== 0 ? sensorFrequency : getFrequencyValue() !== 0 ? getFrequencyValue() : ''}
                    />
                </Box>
            </GridItem>
            <GridItem colSpan={1}>
                <Button
                    colorScheme={getButtonColor()}
                    variant='outline'
                    mt={sensor.isHeadMounted ? "1.5" : ""}
                    size="sm"
                    isDisabled={disableButton() || (isRunning && isGenerable)}
                    onClick={() => {
                        if (allSensorsSelected)
                            handleRemoveAllSensorsButtonClick()
                        else
                            handleSelectAllSensorsButtonClick()
                    }}
                >
                    {getButtonText()}
                </Button>
            </GridItem>
        </Grid>
        {
            sensorExpanded &&
            sensor.isHeadMounted &&
            Array.from(Array(machinery.numHeads)).map((_, indexHead) => 
                <HeadMechEntry
                    key={indexHead}
                    indexHead={indexHead + 1}
                    sensor={sensor}
                    machinery={machinery}
                    sensorFrequency={sensorFrequency}
                    isRunning={isRunning}
                    isGenerable={isGenerable}
                />
            )
        }
        <Divider orientation="horizontal" w="full"/>
        <Spacer />
    </VStack>
    )
}

interface HeadMechEntryProps {
    indexHead: number
    sensor: Sensor
    machinery: Machinery
    sensorFrequency: number
    isRunning: boolean
    isGenerable: boolean
}

function HeadMechEntry(props: HeadMechEntryProps) {

    const {indexHead, sensor, machinery} = props
    const [sensorSelected, setSensorSelected] = useState(false)
    const {configuration, setConfiguration, setIsSaved} = useContext(ConfigurationContext)
    const {sensorFrequency, isRunning, isGenerable} = props

    const getFrequencyValue = () => {
        return configuration.getSensorDataFrequency(machinery.uid, sensor.internalName)
    }

    // CHECK IF SENSOR IS SELECTED
    useEffect(() => {
        const head = configuration.getHeadFromSensorFromMachinery(machinery.uid, sensor.internalName, indexHead)
        if(head) {
            setSensorSelected(true) 
            return
        }
        setSensorSelected(false)
    }, [configuration])


    // SELECT SENSOR BUTTON CLICK
    function handleSelectSensorButtonClick() {
        setIsSaved(false)
        setConfiguration((prevConfig) => {
            const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
            newConfig.addHeadSensorConfToMachinery(machinery.uid, sensor.internalName, sensor.category, indexHead, sensorFrequency)
            return newConfig
        })
    }

    // REMOVE SENSOR BUTTON CLICK
    function handleRemoveSensorButtonClick() {
        setIsSaved(false)
        setConfiguration((prevConfig) => {
            const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
            newConfig.removeHeadSensorConfToMachinery(machinery.uid, sensor.internalName, indexHead)
            return newConfig
        })
    }

    // GET BUTTON TEXT
    function getButtonText() {
        if (isRunning && sensorSelected && isGenerable)
            return 'Generating'

        if (sensorSelected)
            return 'Remove'

        return 'Select'
    }

    // GET BUTTON COLOR - green/red/gray
    function getButtonColor() {
        if (isRunning && sensorSelected && isGenerable)
            return 'black'

        if (sensorSelected)
            return 'red'

        return 'teal'
    }

    function disableButton() {
        if(configuration.getSensorNumHeads(machinery.uid, sensor.internalName)){
            return false
        }
        else {
            if (sensorFrequency === 0 && getFrequencyValue() === 0) {
                return true
            }
            else{
                return false
            }
        }
    }


    return (
        <>
            <HStack
                pl={8}
                mt="1!important"
                w="full"
                justifyContent="space-between"
            >
                <Text fontSize="sm">{`• Head ${indexHead}`}</Text>
                <Button
                    colorScheme={getButtonColor()}
                    size="sm"
                    variant='outline'
                    isDisabled={disableButton() || (isRunning && isGenerable)}
                    onClick={() => {
                        if (sensorSelected)
                            handleRemoveSensorButtonClick()
                        else
                            handleSelectSensorButtonClick()
                    }}
                >
                    {getButtonText()}
                </Button>
            </HStack>
            {
                (indexHead < machinery.numHeads) &&
                <Divider orientation="horizontal" mt="1!important"/>
            }
        </>
    )
}