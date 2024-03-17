import {
    Box,
    Button,
    HStack,
    Input,
    InputGroup,
    InputLeftElement,
    InputRightElement,
    Select,
    Spinner,
    Text,
    VStack,
    Grid,
    GridItem,
    Heading,
    Collapse,
    Spacer,
    Tooltip,
    Modal, 
    ModalOverlay, 
    ModalContent, 
    ModalFooter, 
    ModalBody, 
} from '@chakra-ui/react'
import {FiInfo, FiPlus, FiDatabase} from 'react-icons/fi'
import {useContext, useEffect, useState} from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'
import Machinery from '../../models/Machinery'
import {FiSearch, FiX} from 'react-icons/fi'
import MachineryCard from './MachineryCard'
import SensorCard from './SensorCard'
import Configuration from "../../models/Configuration"
import generateService from "../../services/GenerateService"
import machineryData from '../../database/machinery.json'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'
import toastHelper from '../../utils/ToastHelper'
import axiosExcpetionHandler from '../../utils/AxiosExcpetionHandler'
import LoadConfigurationModal from './LoadConfigurationModal'
import StatsSimulationModal from './StatsSimulationModal'
import SaveConfigurationMenu from './SaveConfiguration'
import './GeneratePanel.css'


interface MachineryActive {
    machinery: Machinery
    active: boolean
  }

export default function GeneratePanel() {
    const [machinerySearch, setMachinerySearch] = useState<{
        searchTerm: string
        highlightTerm: string
        doSearch: boolean
    }>({
        searchTerm: '',
        highlightTerm: '',
        doSearch: false
    })
    const [machinerySort, setMachinerySort] = useState('none')
    const [machineries, setMachineries] = useState<MachineryActive[]>([])
    const [loadingMachineries, setLoadingMachineries] = useState(true)
    const {configuration, setConfiguration, isSaved, setIsSaved, toast} = useContext(ConfigurationContext)
    const [machineriesIsOpen, setMachineriesIsOpen] = useState(true)
    const [sensorsIsOpen, setSensorsIsOpen] = useState(false)
    const [loadConfModalOpen, setloadConfModalOpen] = useState(false)
    const [isTraining, setIsTraining] = useState(false)
    const [isTrained, setIsTrained] = useState(false)
    const [modalTrain, setModalTrain] = useState(false)
    const [isGenerable, setIsGenerable] = useState(false)
    const [isHovered, setIsHovered] = useState(false)
    const [isHoveredNew, setIsHoveredNew] = useState(false)
    const [isRunning, setIsRunning] = useState(false)
    const [statsModalOpen, setstatsModalOpen] = useState(false)
    const [simulationStats, setSimulationStats] = useState({
        message: '',
        samples_generated: -1,
        faults_generated: -1,
        simulation_time: -1,
    })
    
    function handleMachineriesToggle() {
        setMachineriesIsOpen(!machineriesIsOpen)
    }
    
    function handleSensorsToggle() {
        setSensorsIsOpen(!sensorsIsOpen)
    }

    // LOAD MACHINERIES FROM JSON
    useEffect(() => {
        const machineryArray: MachineryActive[] = []

        machineryData.locations.forEach((location: any) => {
            location.equipment.forEach((equipment: any) => {
                const machinery = new Machinery(equipment)
                const machineryActive: MachineryActive = {
                    machinery,
                    active: true
                }
                machineryArray.push(machineryActive)
            })
          })
        
        setLoadingMachineries(false)
        setMachineries(machineryArray)
      }, [])

          // CHECK MODEL STATUS  //////
    useEffect(() => {
        async function getModelStatus() {
            try {
                const response = await generateService.statusModel()
                console.log('Data from the server - model status:', response.data)
                if(response.status === 200) {
                    if (response.data.trained){
                        setIsTrained(true)
                    }
                    else{
                        setIsTrained(false)
                    }
                }
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        getModelStatus()
    }, []) 

    // READ CONFIGURATION ON CONSOLE
    useEffect(() => {
    console.log('Confiuration updated:', configuration)
    }, [configuration]) 

    // HANDLE SEARCH
    useEffect(() => {
        if (!machinerySearch.doSearch) return

        const searchTerm = machinerySearch.searchTerm.toLowerCase()
        setMachineries((val) => {
            val.forEach((machineryActive) => {
                if (!searchTerm ||
                    machineryActive.machinery.uid.toLowerCase().includes(searchTerm) ||
                    machineryActive.machinery.modelName.toLowerCase().includes(searchTerm) ||
                    machineryActive.machinery.modelType.toLowerCase().includes(searchTerm))
                    machineryActive.active = true
                else
                    machineryActive.active = false
            })

            return [...val]
        })

        setMachinerySearch((val) => {
            val.doSearch = false
            val.highlightTerm = val.searchTerm

            return {...val}
        })
    }, [machinerySearch])

    // HANDLE SORT
    useEffect(() => {
        if (machinerySort === 'none') return
        toastHelper.makeToast(
            toast,
            "Sorting applied",
            'info'
        )
        setMachineries((val) => {
            val.sort((a, b) => {
                switch (machinerySort) {
                    case 'uid': {
                        return a.machinery.uid > b.machinery.uid ? 1 : -1
                    }
                    case 'modelName': {
                        return a.machinery.modelName > b.machinery.modelName ? 1 : -1
                    }
                    default: {
                        console.error('Unknown sort term')
                        return 0
                    }
                }
            })

            return [...val]
        })
        setConfiguration((prevConfig) => {
            prevConfig.sortConfigurationMachineries(machinerySort)
            const newConfig = new Configuration( prevConfig.name, [...prevConfig.machineriesSelected])
            return newConfig
        })
         // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [machinerySort])

    // SEARCH TERM CHANGED EVENT
    function handleSearchTermChanged(e : any) {
        setMachinerySearch((val) => {
            val.searchTerm = e.target.value
            return {...val}
        })
    }

    // HANDLE SEARCH BUTTON CLICKED
    function handleSearchButtonClicked() {
        setMachinerySearch((val) => {
            val.doSearch = true

            return {...val}
        })
    }

    // SHOW SensorCard ONLY IF MACHINERY IS ACTIVE AND SELECTED
    function sensorsSection() {
        let isActiveAndSelected = false
        machineries.forEach(mach => {
            if (mach.active && configuration.machineriesSelected.find(selected => selected.uid === mach.machinery.uid)) {
                isActiveAndSelected = true
            }
        })
        return isActiveAndSelected
    }

    function handleOpenLoadConfiguration() {
        setloadConfModalOpen(true)
    }

    // HANDLE TRAIN MODEL BUTTON
    function handleTrainModelButton() {
        async function getModelStatus() {
            try {
                const response = await generateService.statusModel()
                console.log('Data from the server - model status:', response.data)
                if(response.status === 200) {
                    if (response.data.trained){
                        setIsTrained(true)
                        setModalTrain(true)
                    }
                    else{
                        setIsTrained(false)
                        handleTrainModel()
                    }
                }
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        getModelStatus()
    }

    function handleTrainModel() {
        setModalTrain(false)
        setIsTraining(true)
        async function train() {
            try {
                const response = await generateService.trainModel()
                if(response.status === 200) {
                    toastHelper.makeToast(
                        toast,
                        response.data.message,
                        'info'
                    )
                    setIsTrained(true)
                    setIsTraining(false)
                }
            }
            catch (error : any) 
            {
                setIsTraining(false)
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        train()
    }

    // HANDLE RUN SIMULATION BUTTON
    function handleRunSimulation() {
        if (!isTrained){
            toastHelper.makeToast(
                toast,
                "The model is not trained",
                'warning'
            )
        return
        }
        if (isGenerable){
            toastHelper.makeToast(
                toast,
                "The simulation is started",
                'info'
            )
        }
        setIsRunning(true)
        async function runSimulation() {
            try {
                const response = await generateService.runSimulation(
                    JSON.stringify({'machineriesSelected': configuration.machineriesSelected}))
                
                if(response.status === 200) {
                    toastHelper.makeToast(
                        toast,
                        "The simulation is over",
                        'info'
                    )
                    setIsRunning(false)
                    setstatsModalOpen(true)
                    setSimulationStats(response.data)
                }
            }
            catch (error: any) {
                setIsRunning(false)
                axiosExcpetionHandler.handleException(toast, error)
            }
        } 

        runSimulation()
    }
    
    // HANDLE STOP SIMULATION BUTTON
    function handleStopSimulation() {
        async function stopSimulation() {
            try {
                const response = await generateService.stopSimulation()
                if(response.status === 200) {
                    setIsRunning(false)
                    setstatsModalOpen(true)
                }
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        } 
        stopSimulation()
    }

    // ENABLE RUN SIMULATION BUTTON
    useEffect(() => {
        let count = 0
        for (const machinery of configuration.machineriesSelected) {
            if (machinery.sensorsSelected.length > 0 && machinery.faultFrequency !== 0 && machinery.faultProbability !== 0) {
                for (const sensor of machinery.sensorsSelected) {
                    if (sensor.dataFrequency === 0) {
                        setIsGenerable(false)
                        return 
                    }
                }
                count += 1
            }
            else{
                setIsGenerable(false)
                return
            }
        }
        if (count > 0 && configuration.machineriesSelected.length === count && isTrained)
            setIsGenerable(true) 
        else 
            setIsGenerable(false)
        }, [configuration, isTrained])


    return (
        <VStack
            w="full"
            h="full"
            alignItems="space-between"
            spacing={4}
        >
            <HStack
                p={6}
                w="full"
                borderWidth={1}
                borderColor="gray.200"
                bgColor="white"
                rounded="md"
            >
                <InputGroup size='md'>
                    <InputLeftElement
                        pointerEvents='none'
                        color='gray.300'
                        fontSize='1.2em'
                    >
                        <FiSearch/>
                    </InputLeftElement>
                    <Input
                        pr='4.5rem'
                        type="text"
                        placeholder='Search machinery'
                        value={machinerySearch.searchTerm}
                        onChange={handleSearchTermChanged}
                    />
                    <InputRightElement width='6.5rem'>
                        <Box
                            pr={1}
                            _hover={{
                                cursor: 'pointer'
                            }}
                            onClick={() => {
                                setMachinerySearch({
                                    searchTerm: '',
                                    doSearch: true,
                                    highlightTerm: ''
                                })
                            }}
                        >
                        <FiX size={18} color="gray"/>
                        </Box>
                        <Button
                            h='1.75rem'
                            size='sm'
                            colorScheme="blue"
                            onClick={handleSearchButtonClicked}
                        >
                            Search
                        </Button>
                    </InputRightElement>
                </InputGroup>
                <Select
                    w="350px"
                    value={machinerySort}
                    onChange={(e) => {
                        setMachinerySort(e.target.value)
                    }}
                >
                    <option value='none'>Sort by default order</option>
                    <option value='uid'>Sort by machinery ID</option>
                    <option value='modelName'>Sort by machinery model</option>
                </Select>
            </HStack>
            <HStack
                p={4}
                w="full"
                borderWidth={1}
                borderColor="gray.200"
                bgColor="white"
                rounded="md"
                justifyContent="space-between" 
                alignItems="center" 
                >
                <Text mb={1} textAlign="left" fontSize="lg">
                     {configuration.name}
                </Text>
                <Spacer />
                {!isSaved &&
                <Tooltip 
                label={"The actual configuration is not saved"} 
                isOpen={isHoveredNew}
                placement="left"
                >
                <Box
                    onMouseEnter={() => setIsHoveredNew(true)}
                    onMouseLeave={() => setIsHoveredNew(false)}
                    >
                    <FiInfo/>
                </Box>
                </Tooltip>
                }
                <Button
                    leftIcon={<FiPlus/>}
                    colorScheme="blue"
                    color="blue.500"
                    borderColor="blue.500"
                    borderWidth="1px"
                    isDisabled={isGenerable && isRunning}
                    onClick={() => {
                        setIsSaved(true)
                        setConfiguration(new Configuration())   
                    }}
                    bg="gray.100"
                    _hover={{ color: 'white', bg: 'blue.500' }}
                >
                    New Configuration
                </Button>
                <Button
                    leftIcon={<FiSearch/>}
                    colorScheme="teal"
                    color="teal.500"
                    borderColor="teal.500"
                    borderWidth="1px"
                    isDisabled={isGenerable && isRunning}
                    onClick={handleOpenLoadConfiguration}
                    bg="gray.100"
                    _hover={{ color: 'white', bg: 'teal.500' }}
                >
                    Load Configuration
                </Button>
                {loadConfModalOpen && <LoadConfigurationModal 
                    isOpen={loadConfModalOpen}
                    setIsOpen={setloadConfModalOpen} 
                    />}
                <Button
                    leftIcon={<FiDatabase/>}
                    colorScheme="green"
                    color={isTrained ? 'white' : 'green.500'}
                    borderColor={isTrained ? 'green.500' : 'green.500'}
                    borderWidth="1px"
                    bg={isTrained ? 'green.500' : 'gray.100'}
                    onClick={() => {
                        if (!isTraining) {
                            handleTrainModelButton()
                        }
                    }}
                    _hover={{
                        color: isTrained ? 'white' : isTraining ? 'green.500' : 'white',
                        bg: isTrained ? 'green.500' : isTraining ? 'gray.100' : 'green.500',
                    }}
                    isDisabled={isTraining}
                >
                    {isTraining ? (
                        <>
                            Training <Spinner size="sm" ml={2} />
                        </>
                    ) : isTrained ? (
                        'Trained'
                    ) : (
                        'Train Model'
                    )}  
                </Button>
                {modalTrain && 
                <Modal isOpen={modalTrain} onClose={() => setModalTrain(false)} closeOnOverlayClick={true}>
                    <ModalOverlay />
                    <ModalContent>
                        <ModalBody>
                            <Text mt={4} color="gray.700" fontSize="xl" fontWeight="bold">
                                The model is already trained
                            </Text>
                            <Text color="gray.600" mt={2}>
                                Do you want to train it again?
                            </Text>
                        </ModalBody>
                        <ModalFooter>
                            <Button 
                                colorScheme="green" 
                                mr={3} 
                                onClick={handleTrainModel}
                            >
                                Confirm
                            </Button>
                            <Button 
                                colorScheme="blue" 
                                onClick={() => setModalTrain(false)} 
                            >
                                Close
                            </Button>
                        </ModalFooter>
                    </ModalContent>
                </Modal>
            }
            </HStack>
            <HStack justifyContent="left" w="full">
                <Heading mb={1} textAlign="left" fontSize="3xl">
                    Machineries
                </Heading>
                    {machineriesIsOpen ? (
                    <FaChevronUp onClick={handleMachineriesToggle} />
                    ) : (
                    <FaChevronDown onClick={handleMachineriesToggle} />
                    )}
            </HStack>
            <Collapse in={machineriesIsOpen} animateOpacity>
                <Grid
                    templateColumns={{ base: 'repeat(1, 1fr)', md: 'repeat(3, 1fr)', lg: 'repeat(6, 1fr)'}}
                    gap={4}
                >
                    {!loadingMachineries &&
                        machineries
                            .filter((machineryActive) => machineryActive.active)
                            .map((machineryActive) => (
                                <GridItem key={machineryActive.machinery.uid}>
                                    <MachineryCard 
                                        key={machineryActive.machinery.modelName}
                                        machinery={machineryActive.machinery} 
                                        isRunning={isRunning}
                                        isGenerable={isGenerable}
                                        highlightTerm={machinerySearch.highlightTerm}/>
                                </GridItem>
                            ))}
                </Grid>
            </Collapse>
            {!loadingMachineries &&
            machineries
                .filter((machinery) => machinery.active)
                .length === 0 && (
                <HStack
                    w="full"
                    h="200px"
                    justifyContent="center"
                    alignItems="center"
                >
                {machinerySearch.highlightTerm && (
                    <Text>Nothing matches your search term</Text>
                )}
                {!machinerySearch.highlightTerm && <Text>No machineries available</Text>}
                </HStack>
            )}
            {loadingMachineries && (
            <VStack
                w="full"
                h="300px"
                justifyContent="center"
                alignItems="center"
            >
                <Spinner size="xl" />
            </VStack>
            )}
            <>
            <HStack justifyContent="left"  w="full"
                className={`transition-sensors ${
                    sensorsSection() ? 'visible' : 'hidden'
                }`}>
                <Heading mb={1} textAlign="left" fontSize="3xl">
                    Sensors
                </Heading>
                {sensorsIsOpen ? (
                    <FaChevronUp onClick={handleSensorsToggle} />
                    ) : (
                    <FaChevronDown onClick={handleSensorsToggle} />
                    )}
            </HStack>
            <Collapse in={sensorsIsOpen} animateOpacity>
                <div className={`grid-container ${
                        sensorsSection() ? 'visible' : 'hidden'}`}
                    >
                    {configuration.machineriesSelected.map((machinerySelected, index) => {
                        const machineryActive = machineries.find(
                            (mach) => mach.machinery.uid === machinerySelected.uid && mach.active
                        )
                        return machineryActive ? (
                            <div 
                                key={`${machineryActive.machinery.modelType}-${machineryActive.machinery.modelName}-${machineryActive.machinery.uid}`}
                                className={`grid-item`}
                            >
                                <SensorCard 
                                    key={`${machineryActive.machinery.modelType}-${machineryActive.machinery.uid}`} 
                                    machinery={machineryActive.machinery} 
                                    isRunning={isRunning}
                                    isGenerable={isGenerable}
                                    highlightTerm={machinerySearch.highlightTerm}
                                />
                            </div>
                        ) : null
                        })
                    }
                </div>
            </Collapse>
            </>
            <>
            <HStack
                p={4}
                w="full"
                borderWidth={1}
                borderColor="gray.200"
                bgColor="white"
                rounded="md"
                justifyContent="space-between" 
            >
                <SaveConfigurationMenu/>
                <Spacer />
                {!isGenerable &&
                <Tooltip 
                    label={"Train the model ensuring that at least one machine and one sensor are selected, and set a fault frequency and probability for each selected machine."} 
                    isOpen={isHovered}
                    placement="left"
                >
                    <Box
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                    >
                    <FiInfo/>
                    </Box>
                    </Tooltip>
                }
                <Button
                    colorScheme={isGenerable ? "green" : "orange"}
                    borderColor={isGenerable ? "green.500" : "orange.500"}
                    borderWidth="1px"
                    bg={isRunning? 'green.500' : 'gray.100'}
                    color={isRunning? 'white' : isGenerable ? 'green.500' : 'orange.500'}
                    onClick={() => {
                        if (!isRunning) {
                            handleRunSimulation()
                        }
                    }}
                    _hover={{ 
                        color: 'white', 
                        bg: isGenerable ? 'green.500' : 'orange.500'
                    }}
                    _disabled={{
                        color: "white",
                        borderColor: isGenerable ? "green.600" : "orange.600",
                        bg: "white.500", 
                        cursor: "not-allowed", 
                        pointerEvents: "none", 
                    }}
                >
                    {isGenerable && isRunning ? (
                        <>
                            <Spinner size="sm" color="white.500" mr={2} />
                            Running
                        </>
                    ) : (
                        'Start Simulation'
                    )}
                </Button>
                <Button
                    colorScheme="red"
                    color="white"
                    borderColor="red.500"
                    borderWidth="1px"
                    isDisabled={!isRunning || !isGenerable}
                    onClick={handleStopSimulation}
                    bg="red.500"
                    _hover={{ color: 'white', bg: 'red.500' }}
                    _disabled={{
                        color: "white",
                        borderColor: "gray.600",
                        bg: "gray.500", 
                        cursor: "not-allowed", 
                        pointerEvents: "none", 
                    }}
                >
                Stop
                </Button>
                {statsModalOpen && <StatsSimulationModal 
                    isOpen={statsModalOpen}
                    simulationStats={simulationStats}
                    setSimulationStats={setSimulationStats}
                    setIsOpen={setstatsModalOpen} />}
            </HStack>
            </>
    </VStack>
)}