import { 
  Text,
  Box,
  Button, 
  Menu, 
  MenuButton, 
  MenuList, 
  MenuItem, 
  Portal,
  Modal, 
  ModalOverlay, 
  ModalContent, 
  ModalHeader,
  ModalFooter, 
  ModalBody, 
  ModalCloseButton, 
  Input
 } from '@chakra-ui/react'
import { useState, useContext, useEffect } from 'react'
import { FiSave, FiChevronDown, FiEdit } from 'react-icons/fi'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'
import generateService from "../../services/GenerateService"
import Configuration from '../../models/Configuration'
import toastHelper from '../../utils/ToastHelper'
import axiosExcpetionHandler from '../../utils/AxiosExcpetionHandler'


export default function SaveConfigurationMenu() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isSavable, setIsSavable] = useState(false)
  const {configuration, setConfiguration, setIsSaved, toast} = useContext(ConfigurationContext)
  const [isOpen, setIsOpen] = useState(false)
  const [isPresent, setIsPresent] = useState(false)
  const [newName, setNewName] = useState("")

  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  // HANDLE SAVE CONFIGURATION
    function SaveConfiguration() {
        async function save() {
            try {
                const response = await generateService.updateConfiguration(configuration.name,
                        JSON.stringify({'machineriesSelected': configuration.machineriesSelected}))
                if(response.status === 204)
                    toastHelper.makeToast(
                        toast,
                        'No update to save',
                        'success'
                    )
                else if(response.status === 200)
                    toastHelper.makeToast(
                        toast,
                        response.data.message,
                        'success'
                    )
                else if(response.status === 404){
                    const response_insert = await generateService.insertConfiguration(
                        JSON.stringify({ name: configuration.name, machineriesSelected: configuration.machineriesSelected }))
                        toastHelper.makeToast(
                            toast,
                            "Configuration saved",
                            'success'
                        )
                    }
                setIsSaved(true)
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        save()

    }
  
    function SaveAsConfiguration() {
        setIsOpen(!isOpen)
    }
  
    // HANDLE SAVE AS CONFIGURATION
    function handleSaveAsConfiguration() {
        async function saveAs() {
            try {
                const response_get = await generateService.getConfiguration(newName)
                if(response_get.status === 404){
                    const newConfig = new Configuration(newName, [...configuration.machineriesSelected])
                    const response_insert = await generateService.insertConfiguration(
                        JSON.stringify({ name: newConfig.name, machineriesSelected: newConfig.machineriesSelected }))
                        setConfiguration(newConfig)
                        setNewName("")
                        setIsSaved(true)
                        setIsPresent(false)
                        setIsOpen(!isOpen)
                        toastHelper.makeToast(
                            toast,
                            response_insert.data.message,
                            'success'
                        )
                }
                else if(response_get.status === 200)

                    setIsPresent(true)
            } 
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        saveAs()
    }

    // HANDLE CONFIRM SAVE CONFIGURATION
    function handleConfirmSave() {
        async function saveConfirm() {
            try {
                const newConfig = new Configuration(newName, [...configuration.machineriesSelected])
                const response_insert = await generateService.updateConfiguration(newConfig.name,
                    JSON.stringify({'machineriesSelected': configuration.machineriesSelected}))
                if(response_insert.status === 200){
                    setConfiguration(newConfig)
                    setNewName("")
                    setIsSaved(true)
                    setIsPresent(false)
                    setIsOpen(false)
                    toastHelper.makeToast(
                        toast,
                        "Configuration overwritten with success",
                        'success'
                    )
                }
            }
            catch (error : any) {
                axiosExcpetionHandler.handleException(toast, error)
            }
        }
        saveConfirm()
    }

    // ENABLE SAVE BUTTON
    useEffect(() => {
        if(configuration.machineriesSelected.length === 0){
            setIsSavable(false)
            return
        }
        else{
            configuration.machineriesSelected.forEach(machinery => {
                if(machinery.sensorsSelected.length > 0 && machinery.getFaultFrequency() !== 0 && machinery.getFaultProbability())
                    setIsSavable(true)
            })
        }
    }, [configuration])

  

    return (
        <Menu>
        <MenuButton
            as={Button}
            leftIcon={<FiSave />}
            rightIcon={<FiChevronDown />}
            colorScheme="blue"
            variant="ghost"
            ml="0!important"
            onClick={handleMenuToggle}
        >
            Save configuration
        </MenuButton>
        <Portal>
            <MenuList shadow="2xl">
            <MenuItem
            icon={<FiSave />}
            isDisabled={!isSavable || configuration.name === 'Unsaved configuration'}
            title={
                !isSavable
                ? 'No sensors selected'
                : configuration.name === 'Unsaved configuration'
                ? 'The configuration has no name'
                : ''
            }
            onClick={() => {
                SaveConfiguration()
                handleMenuToggle()
            }}
            >
            Save
            </MenuItem>
            <MenuItem
                icon={<FiEdit />}
                isDisabled={!isSavable}
                title={!isSavable ? 'No sensors selected' : ''}
                onClick={() => {
                SaveAsConfiguration()
                handleMenuToggle()
                }}
            >
                Save as
                <Modal isOpen={isOpen} onClose={() =>{setNewName("") 
                                                    setIsPresent(false)
                                                    setIsOpen(false)}}
                    closeOnOverlayClick={false}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Save As Configuration</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                    <Input
                        placeholder="Enter new configuration name"
                        value={newName}
                        onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            handleSaveAsConfiguration()
                        }
                        }}
                        onChange={(e) =>{ setNewName(e.target.value)
                                        if (e.target.value === "")
                                    setIsPresent(false) 
                                        }}
                    />

                    {isPresent && 
                    <Box mt="4">
                    <Text color="red" fontWeight="bold" fontSize="sm">
                        A configuration with this name is already saved.
                    </Text>
                    <Text color="red" fontWeight="bold" fontSize="sm">
                        Are you sure you want to overwrite it?
                    </Text>
                    </Box>
                    }
                    </ModalBody>
                    <ModalFooter>
                    {isPresent &&<Button colorScheme="green" mr={3} onClick={handleConfirmSave}>
                        Save
                    </Button>}
                    </ModalFooter>
                </ModalContent>
                </Modal>
            </MenuItem>
            </MenuList>
        </Portal>
        </Menu>
    )
}

