import { 
    Spinner, 
    Grid, 
    Modal, 
    GridItem, 
    ModalOverlay, 
    ModalContent, 
    ModalHeader, 
    ModalFooter, 
    ModalBody, 
    ModalCloseButton, 
    Button
} from '@chakra-ui/react'
import React, {useContext} from 'react'
import ConfigurationContext from '../../utils/contexts/ConfigurationContext'

interface StatsModalProps {
    isOpen: boolean
    setIsOpen: React.Dispatch<React.SetStateAction<boolean>>
    simulationStats: {
        message: string
        samples_generated: number
        faults_generated: number
        simulation_time: number
    }
    setSimulationStats: React.Dispatch<React.SetStateAction<{
        message: string
        samples_generated: number
        faults_generated: number
        simulation_time: number
    }>>
}

export default function StatsSimulationModal(props : StatsModalProps) {
    const {isOpen, setIsOpen, simulationStats, setSimulationStats} = props
    const {configuration} = useContext(ConfigurationContext)

    // HANDLE CONVERSION ss TO mm:ss
    function formatTime(totalSeconds: number) {
        const minutes = Math.floor(totalSeconds / 60)
        const seconds = totalSeconds % 60
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`
    }

    const onClose = () => {
        setSimulationStats({
            message: '',
            samples_generated: -1,
            faults_generated: -1,
            simulation_time: -1,
        })
        setIsOpen(false)
    }

return (
    <Modal isOpen={isOpen} onClose={onClose} closeOnOverlayClick={false}>
        <ModalOverlay/>
        <ModalContent>
            <ModalHeader>Simulation resume</ModalHeader>
            <ModalCloseButton />
            <ModalBody display="flex" flexDirection="column">
            {simulationStats.samples_generated === -1 ? (
                <Spinner size="xl" alignSelf="center" />
            ) : (
                <Grid templateColumns="repeat(2, 1fr)" gap={2}>
                <GridItem textAlign="left">Configuration name:</GridItem>
                <GridItem textAlign="left">{configuration.name}</GridItem>

                <GridItem textAlign="left">Machines:</GridItem>
                <GridItem textAlign="left">{configuration.machineriesSelected.length}</GridItem>

                <GridItem textAlign="left">Samples generated:</GridItem>
                <GridItem textAlign="left">{simulationStats.samples_generated}</GridItem>

                <GridItem textAlign="left">Faults generated:</GridItem>
                <GridItem textAlign="left">{simulationStats.faults_generated}</GridItem>

                <GridItem textAlign="left">Simulation time:</GridItem>
                <GridItem textAlign="left">{formatTime(simulationStats.simulation_time)}</GridItem>
                </Grid>
            )}
            </ModalBody>
            <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
                Close
            </Button>
            </ModalFooter>
        </ModalContent>
    </Modal>
)}
  