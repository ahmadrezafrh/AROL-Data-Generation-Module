import {Heading, HStack, Image, Text, VStack, Box, Checkbox} from '@chakra-ui/react'
import {useContext, useState, useEffect} from 'react'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'
import type Machinery from '../../models/Machinery'
import Configuration from '../../models/Configuration'
import helperFunctions from '../../utils/HelperFunctions'


interface MachineryCardProps {
    machinery: Machinery
    isRunning: boolean
    isGenerable: boolean
    highlightTerm: string
}

export default function MachineryCard(props: MachineryCardProps) {

    const {machinery, isRunning, highlightTerm, isGenerable} = props
    const {configuration, setConfiguration, setIsSaved} = useContext(ConfigurationContext)
    const [isChecked, setChecked] = useState(false)

    // HANDLE READ CONFIGURATION
    function handleCheck() {
        setChecked((prevChecked) => !prevChecked)
        setIsSaved(false)
        setConfiguration((prevConfig) => {
            const newConfig = new Configuration(prevConfig.name, [...prevConfig.machineriesSelected])
            if (!isChecked) {
                newConfig.addMachineriesSelected(machinery.uid, machinery.modelName)
            } else {    
                newConfig.removeMachineriesSelected(machinery.uid)
            }
            return newConfig
        })
      }

    // HANDLE READ CONFIGURATION
    useEffect(() => {
        if (configuration.machineriesSelected.length === 0){
            setChecked(false)
            return
        }
        const mach = configuration.getMachinery(machinery.uid)
        if (mach) 
            setChecked(true)
        else
            setChecked(false)
    }, [configuration])


    return (
        <VStack
        p={5}
        w="full"
        borderWidth={1}
        borderColor="gray.300"
        bgColor="white"
        rounded="md"
    >
        <Box w="18vh" h="18vh" mb={4}>
            <Image
                boxSize="full"
                objectFit="contain"
                src={require(`./../../assets/machineries/${machinery.modelID}.png`)}
            />
        </Box>
        <VStack
            w="full"
            alignItems="center"
            justifyContent="space-between"
        >
            <VStack alignItems="center" mb={4}>
                <Heading fontSize="md" fontFamily="body" fontWeight={450} color="gray.600" whiteSpace="nowrap">
                    {helperFunctions.highlightText(machinery.uid, 450, highlightTerm)}
                </Heading>
                <Heading
                    fontSize="l"
                    fontFamily="body"
                    fontWeight={550}
                    whiteSpace="nowrap"
                >
                    {helperFunctions.highlightText(machinery.modelName, 550, highlightTerm)}
                </Heading>
                <HStack alignItems="center" justifyContent="center"  w="full" mb={-4}>
                    <Text fontWeight={300} color="gray.500" whiteSpace="nowrap" fontSize="sm">
                        Heads number
                    </Text>
                    <Text
                        color="black"
                        fontSize="md"
                        fontWeight={400}
                        whiteSpace="nowrap"
                    >
                        {helperFunctions.highlightText(machinery.numHeads.toString(), 400, highlightTerm)}
                    </Text>
                </HStack>
            </VStack>
            <HStack justifyContent="center" alignItems="center">
            <Checkbox
                isDisabled={isGenerable && isRunning}
                isChecked={isChecked}
                colorScheme="blue"
                onChange={handleCheck}
                borderColor="blue.500"  
                _disabled={{
                    filter: "brightness(80%)", 
                    cursor: "not-allowed", 
                  }}
            />
        </HStack>
        </VStack>
    </VStack>
)}
     