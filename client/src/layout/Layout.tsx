import {Box, useDisclosure} from '@chakra-ui/react'
import Sidebar from './Sidebar'
import Navbar from './Navbar'
import Router from '../router/Router'
import React, {useContext, useMemo} from 'react'
import SidebarStatusContext from '../utils/contexts/SidebarStatusContext'

export default function Layout() {
    const {sidebarStatus} = useContext(SidebarStatusContext)

    const {isOpen, onOpen, onClose} = useDisclosure()

    const marginLeft = useMemo(
        () => {
            if (sidebarStatus.status === 'open')
                return '279px'

            return '65px'
        },
        [sidebarStatus.status]
    )

    const displaySidebar = useMemo(
        () => sidebarStatus.type !== 'none',
        [sidebarStatus.type]
    )

    return (
        <Box minH="100vh" bg="gray.200">
            {
                displaySidebar &&
                <Sidebar isOpen={isOpen} onOpen={onOpen} onClose={onClose}/>
            }
            <Navbar/>
            <Box ml={{base: 0, md: marginLeft}} p="4">
                <Router/>
            </Box>
        </Box>
    )
}

