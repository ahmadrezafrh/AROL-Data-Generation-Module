import {
    Box,
    type BoxProps,
    Drawer,
    DrawerContent,
    Flex,
    type FlexProps,
    Icon,
    Image,
} from '@chakra-ui/react'
import {FiChevronLeft, FiChevronRight, FiCodesandbox, FiFolder, FiGrid, FiHome, FiLock, FiUsers} from 'react-icons/fi'
import ArolLogo from '../assets/arol-logo.png'
import {Link as RouterLink, useLocation, useNavigate} from 'react-router-dom'
import React, {memo, useContext, useEffect, useMemo, useState} from 'react'
import SidebarStatusContext from '../utils/contexts/SidebarStatusContext'
import {type IconType} from 'react-icons'
import {FiDatabase} from 'react-icons/fi'

const sidebarItems = [
    {name: 'Home', icon: FiHome, link: '/', selectedMatcher: '/'},
    {name: 'Machineries', icon: FiCodesandbox, link: '/machineries', selectedMatcher: '/machiner'},
    {name: 'Dashboards', icon: FiGrid, link: '/dashboards', selectedMatcher: '/dashboards'},
    {name: 'Documents', icon: FiFolder, link: '/documents', selectedMatcher: '/documents'},
    {name: 'Users management', icon: FiUsers, link: '/users', selectedMatcher: '/users'},
    {name: 'Machinery permissions', icon: FiLock, link: '/permissions', selectedMatcher: '/permissions'},
    {name: 'Generate Data', icon: FiDatabase, link: '/generate', selectedMatcher: '/generate'}
]


interface SidebarProps extends BoxProps {
    onClose: () => void
}

export default function Sidebar(props: any) {

    const {onClose, isOpen} = props;

    const {sidebarStatus} = useContext(SidebarStatusContext)


    const displaySidebar = useMemo(
        () => (sidebarStatus.type === 'sidebar'),
        [sidebarStatus.type]
    )

    return (
        <>
            {displaySidebar &&
                <SidebarContent
                    onClose={() => onClose}
                    display="block"
                />
            }
            <Drawer
                autoFocus={false}
                isOpen={isOpen}
                placement="left"
                onClose={onClose}
                returnFocusOnClose={false}
                onOverlayClick={onClose}
                size="full"
            >
                <DrawerContent>
                    {displaySidebar && <SidebarContent onClose={onClose}/>}
                </DrawerContent>
            </Drawer>
        </>
    )
}

const SidebarContent = memo(({...rest}: SidebarProps) => {
    const navigate = useNavigate()
    const {sidebarStatus, dispatchSidebar} = useContext(SidebarStatusContext)

    // SIDEBAR EXPAND/COLLAPSE HANDLER
    function handleSidebarExpandCollapse() {
        if (sidebarStatus.status === 'open')
            dispatchSidebar({type: 'sidebar-close'})
        else
            dispatchSidebar({type: 'sidebar-open'})
    }

    useEffect(() => {
        navigate('/generate');
    }, [navigate]);

    return (
        <Box
            // transition="0.5s ease"
            bg="white"
            borderRight="1px"
            borderRightColor="gray.200"
            w={sidebarStatus.status === 'open' ? '279px' : '65px'}
            pos="fixed"
            h="full"
            {...rest}
        >
            <Flex
                h="20"
                alignItems="center"
                mx={sidebarStatus.status === 'open' ? 8 : 0}
                my={8}
                justifyContent="space-between"
                _hover={{
                    cursor: 'pointer'
                }}
                onClick={() => {
                    navigate('/')
                }}
            >
                <Image
                    objectFit='cover'
                    src={ArolLogo}
                    alt='Arol logo'
                    transform={sidebarStatus.status === 'open' ? '' : 'rotate(90deg)'}
                />
            </Flex>
            <Box
                position="absolute"
                top="20px"
                right="-17px"
                bgColor="white"
                borderWidth="1px 1px 1px 0px"
                borderColor="gray.200"
                py={2}
                _hover={{
                    cursor: 'pointer'
                }}
                onClick={handleSidebarExpandCollapse}
            >
                {sidebarStatus.status === 'open' && <FiChevronLeft/>}
                {sidebarStatus.status === 'closed' && <FiChevronRight/>}
            </Box>
            {sidebarItems.map((sidebarItem) => (
                <SidebarItem
                    key={sidebarItem.name}
                    name={sidebarItem.name}
                    icon={sidebarItem.icon}
                    link={sidebarItem.link}
                    selectedMatcher={sidebarItem.selectedMatcher}
                />
            ))}
        </Box>
    )
})

interface NavItemProps extends FlexProps {
    name: string
    icon: IconType
    link: string
    selectedMatcher: string
}

const SidebarItem = (props: NavItemProps) => {

    const {name, icon, link, selectedMatcher} = props;

    const location = useLocation()

    const {sidebarStatus} = useContext(SidebarStatusContext)

    const [isSelected, setIsSelected] = useState(false)
    const [showItem, setShowItem] = useState(true)

    // CHECK IF SIDEBAR ITEM IS TO DISPLAYED
    useEffect(() => {
        setShowItem(true)
    }, [name])

    // CHECK IF SIDEBAR ITEM IS TO BE SELECTED
    useEffect(() => {
        
            if (selectedMatcher === '/')
                setIsSelected(location.pathname === selectedMatcher)
            else
                setIsSelected(location.pathname.startsWith(selectedMatcher))
    }, [location.pathname, selectedMatcher])
 
    return (
        <Box style={{ textDecoration: 'none' }} _focus={{ boxShadow: 'none' }}>
        {name === "Generate Data" ? (
        <RouterLink to={link} hidden={!showItem}>
            <Box style={{textDecoration: 'none'}} _focus={{boxShadow: 'none'}}>
                <Flex
                align="center"
                p="4"
                mx="2"
                borderRadius="lg"
                role="group"
                cursor={name === "Generate Data" ? "pointer" : "not-allowed"}
                _hover={{
                    bg: 'cyan.400',
                    color: 'white'
                }}
                bg={isSelected ? 'gray.400' : ''}
                color={isSelected ? 'white' : ''}
            >
                <Icon
                    mr="4"
                    fontSize="16"
                    _groupHover={{
                        color: 'white'
                    }}
                    as={icon}
                />
                {sidebarStatus.status === 'open' && name}
            </Flex>
        </Box>
        </RouterLink>
        ) : (
        <Box style={{textDecoration: 'none'}} _focus={{boxShadow: 'none'}}>
            <Flex
                align="center"
                p="4"
                mx="2"
                borderRadius="lg"
                role="group"
                cursor={name === "Generate Data" ? "pointer" : "not-allowed"}
                // _hover={{
                //     bg: 'cyan.400',
                //     color: 'white'
                // }}
                bg={isSelected ? 'gray.400' : ''}
                color={isSelected ? 'white' : ''}
            >
                <Icon
                    mr="4"
                    fontSize="16"
                    // _groupHover={{
                    //     color: 'white'
                    // }}
                    as={icon}
                />
                {sidebarStatus.status === 'open' && name}
            </Flex>
        </Box>
        )}
    </Box>
    );
};

