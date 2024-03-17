import { 
    Spinner, 
    IconButton, 
    Modal, 
    ModalOverlay, 
    ModalContent, 
    ModalHeader, 
    ModalFooter, 
    ModalBody, 
    ModalCloseButton, 
    Button, 
    Divider, 
    Text, 
    Box, 
    HStack, 
    VStack,
    InputGroup,
    InputLeftElement,
    Input,
    InputRightElement,
} from '@chakra-ui/react'
import React, {useEffect, useState, useContext} from 'react'
import {FaTimes} from 'react-icons/fa'
import {FiSearch, FiX} from 'react-icons/fi'
import generateService from "../../services/GenerateService"
import Configuration from "../../models/Configuration"
import toastHelper from '../../utils/ToastHelper'
import axiosExcpetionHandler from '../../utils/AxiosExcpetionHandler'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'
import helperFunctions from '../../utils/HelperFunctions'


interface nameActive {
    name: string
    active: boolean
}

interface ConfigurationModalProps {
    isOpen: boolean
    setIsOpen: React.Dispatch<React.SetStateAction<boolean>>
}

export default function LoadConfigurationModal(props : ConfigurationModalProps) {
    const [configutationSearch, setConfigurationSearch] = useState<{
        searchTerm: string
        highlightTerm: string
        doSearch: boolean
    }>({
        searchTerm: '',
        highlightTerm: '',
        doSearch: false
    })
    const {isOpen, setIsOpen} = props
    const {setConfiguration, isSaved, setIsSaved, toast} = useContext(ConfigurationContext)
    const [configurationsNames, setconfigurationsNames] = useState<nameActive[]>([])
    const [isChosen, setIsChosen] = useState(false)
    const [confChosen, setConfChosen] = useState(new Configuration())
    const [loadingConfigurations, setLoadingConfigurations] = useState(true)


    // HANDLE LOAD CONFIGURATION
    const handleLoadConfiguration = (name: string) => {
        async function load() {
            try {
                const nameToLoad = name
                const response = await generateService.getConfiguration(nameToLoad)
                if(response.status === 200) {
                    const conf = new Configuration(response.data.configuration.name, response.data.configuration.machineriesSelected, true)
                    if(!isSaved) {
                        setIsChosen(true)
                        setConfChosen(conf)
                    }
                    else {
                        toastHelper.makeToast(
                            toast,
                            "Configuration loaded",
                            'success'
                        )
                        setConfiguration(conf)
                        setIsOpen(false)
                    }
                }
            }

            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        load()
    }

    // HANDLE LOAD CONFIGURATION BUTTON
    function handleLoadConfigurationButton() {
        toastHelper.makeToast(
            toast,
            "Configuration loaded",
            'success'
        )
        setIsSaved(true)
        setConfiguration(confChosen)
        setIsOpen(false)
    }

    // lOAD CONFIGURATIION NAMES WHEN OPEN
    useEffect(() => {
        async function getNames() {
            try {
                const response = await generateService.getConfigurationsNames()
                const configurationsNames: nameActive[] = []
                if(response.status === 200) {
                    response.data.configurationsNames.forEach((name : string) => {
                        const nameActive: nameActive = {
                        name,
                        active: true
                    }
                        configurationsNames.push(nameActive)
                    })
                    setconfigurationsNames(configurationsNames) 
                    setLoadingConfigurations(false)
                }
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        getNames()

    }, [isOpen]) 
    
    // HANDLE DELETE CONFIGURATION
    function handleDeleteConfiguration(name : string) {
        const nametoDelete = name
        async function deleteConf() {
            try {
                const response = await generateService.deleteConfiguration(nametoDelete)
                if(response.status === 200) {
                    toastHelper.makeToast(
                        toast,
                        response.data.message,
                        'success'
                    )
                const updatedConfigurations = configurationsNames.filter(
                    (nameActive) => nameActive.name !== nametoDelete)
                setconfigurationsNames(updatedConfigurations)
                }
            } 
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        deleteConf()
    }

    function onClose() {
        setIsOpen(false)
    }

    // HANDLE SEARCH
    useEffect(() => {
        if (!configutationSearch.doSearch) return

        const searchTerm = configutationSearch.searchTerm.toLowerCase()
        setconfigurationsNames((val) => {
            val.forEach((el) => {
                if (!searchTerm ||
                    el.name.toLowerCase().includes(searchTerm))
                    el.active = true
                else
                    el.active = false
            })

            return [...val]
        })

        setConfigurationSearch((val) => {
            val.doSearch = false
            val.highlightTerm = val.searchTerm

            return {...val}
        })
    }, [configutationSearch])

    function handleSearchButtonClicked() {
        setConfigurationSearch((val) => {
            val.doSearch = true

            return {...val}
        })
    }

    function handleSearchTermChanged(e : any) {
        setConfigurationSearch((val) => {
            val.searchTerm = e.target.value

            return {...val}
        })
    }
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} closeOnOverlayClick={false}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Saved Configurations</ModalHeader>
        <ModalCloseButton />
        <ModalBody display="flex" flexDirection="column">
          {loadingConfigurations ? ( 
            <Spinner size="xl" alignSelf="center" />
          ) : configurationsNames.length === 0 ? (
            <Text mt={4} fontStyle="italic" color="gray.500" textAlign="center">
              No configurations saved
            </Text>
          ) : (
            <VStack>
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
                        placeholder='Search configuration'
                        value={configutationSearch.searchTerm}
                        onChange={handleSearchTermChanged}
                    />
                    <InputRightElement width='6.5rem'>
                        <Box
                            pr={1}
                            _hover={{
                                cursor: 'pointer'
                            }}
                            onClick={() => {
                              setConfigurationSearch({
                                    searchTerm: '',
                                    doSearch: true,
                                    highlightTerm: ''
                                })
                            }}
                        >
                            <FiX size={15} color="gray"/>
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
          <Box
            w="full"
            maxH="200px"
            overflowY="auto"
            border="1px"
            borderColor="gray.100"
            bg="white"
            pl="4" 
            borderRadius="lg"  // Imposta i bordi arrotondati
          >
         {configurationsNames.filter((nameActive) => nameActive.active)
              .map((nameActive, index) => (
              <Box key={nameActive.name} p="0" m="0">
              <HStack spacing="2">
                <Text cursor="pointer" mb="2" mt="2" _hover={{ bg: '#f0f0f0' }} width="100%" onClick={() => handleLoadConfiguration(nameActive.name)}>
                  {helperFunctions.highlightText(nameActive.name, 450, configutationSearch.highlightTerm)}  
                </Text>
                <IconButton
                  icon={<FaTimes />}
                  aria-label="Delete Configuration"
                  color="red.500"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteConfiguration(nameActive.name)
                  }}
                />
              </HStack>
              {index < configurationsNames.length - 1 && <Divider />} 
            </Box>
            ))}
              {configurationsNames.filter((nameActive) => nameActive.active).length === 0 && (
                <Text m={4} fontStyle="italic" color="gray.500" textAlign="center">
                  Nothing matches your search term
                </Text>
          )}
          </Box>
          </VStack>
        )}
        {isChosen && 
        <Box mt="4">
          <Text color="red" fontWeight="bold" fontSize="sm">
            The actual configuration is not saved.
          </Text>
          <Text color="red" fontWeight="bold" fontSize="sm">
            Are you sure you want to load {confChosen.name}?
          </Text>
        </Box>
        }
        </ModalBody>
        <ModalFooter>
        {isChosen && <Button colorScheme="green" mr={3} onClick={handleLoadConfigurationButton}>
            Load
          </Button>}
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
)}
  