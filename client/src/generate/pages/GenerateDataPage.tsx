import { Box, Heading, HStack } from '@chakra-ui/react'
import GeneratePanel from '../components/GeneratePanel'

export default function GenerateDataPage () {
  return (

        <Box w="full">
            <Heading mb={6}>Generate Data</Heading>
            <HStack
                w="full"
            >
                <GeneratePanel/>
            </HStack>
        </Box>

  )
}
