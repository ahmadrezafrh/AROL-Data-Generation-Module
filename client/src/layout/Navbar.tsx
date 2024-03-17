import {
    Avatar,
    Box,
    Button,
    Flex,
    Heading,
    HStack,
    IconButton,
    Menu,
    MenuButton,
    MenuItem,
    MenuList,
    Text,
    VStack
} from '@chakra-ui/react'
import {FiBell, FiChevronDown, FiLogOut, FiUser} from 'react-icons/fi'
import React, {useContext, useState} from 'react'
import {useNavigate} from 'react-router-dom'
import SidebarStatusContext from '../utils/contexts/SidebarStatusContext'


interface Company {
    id: number
    name: string
}

export default function Navbar() {
    const navigate = useNavigate()

    const {sidebarStatus} = useContext(SidebarStatusContext)

    const [company, setCompany] = useState<Company | null>()

    // FETCH COMPANY DETAILS
    // useEffect(() => {
    //     if ((principal == null) || !principal.companyID)
    //         return

    //     async function getData() {
    //         const result = await companyService.getCompanyByPrincipal()

    //         setCompany(result)
    //     }

    //     getData()
    // }, [principal])

    return (
        <Flex
            px={4}
            height="20"
            alignItems="center"
            bg="white"
            borderBottomWidth="1px"
            borderBottomColor="gray.200"
            justifyContent={{base: 'space-between', md: 'flex-end'}}
        >
            {
                <HStack
                    pl={sidebarStatus.status === 'open' ? '289px' : '75px'}
                    w="full"
                    spacing={{base: '0', md: '6'}}
                    justifyContent="space-between"
                >
                    <Box
                        _hover={{
                            cursor: 'pointer'
                        }}
                    >
                        <Heading
                            size="md"
                        >
                            {(company != null) ? company.name : 'AROL'}
                        </Heading>
                    </Box>
                    <HStack>
                        <IconButton
                            size="lg"
                            variant="ghost"
                            aria-label="open menu"
                            icon={<FiBell/>}
                        />
                        <Flex alignItems="center">
                            <Menu>
                                <MenuButton
                                    py={2}
                                    transition="all 0.3s"
                                    _focus={{boxShadow: 'none'}}>
                                    <HStack>
                                        <Avatar
                                            size="sm"
                                            name="Name Surname"
                                        />
                                        <VStack
                                            display={{base: 'none', md: 'flex'}}
                                            alignItems="flex-start"
                                            spacing="1px"
                                            ml="2">
                                            <Text fontSize="md">Name Surname</Text>
                                            <Text fontSize="xs" color="gray.600" fontWeight={500}>
                                                Role
                                            </Text>
                                        </VStack>
                                        <Box display={{base: 'none', md: 'flex'}}>
                                            <FiChevronDown/>
                                        </Box>
                                    </HStack>
                                </MenuButton>
                                <MenuList
                                    bg="white"
                                    borderColor="gray.200">
                                    {/* <MenuItem>Settings</MenuItem> */}
                                    {/* <MenuDivider/> */}
                                    <MenuItem
                                        icon={<FiLogOut/>}
                                    >
                                        Sign out
                                    </MenuItem>
                                    <MenuItem
                                        icon={<FiUser/>}
                                        // onClick={handleSignOut}
                                    >
                                        My account
                                    </MenuItem>
                                </MenuList>
                            </Menu>
                        </Flex>
                    </HStack>
                </HStack>
            }
            {
                <HStack>
                    <Button
                        colorScheme="blue"
                        variant="outline"
                    >
                        Login
                    </Button>
                    {/* <Button */}
                    {/*    colorScheme={"blue"} */}
                    {/*    onClick={handleSignupButtonClick} */}
                    {/* > */}
                    {/*    Sign up */}
                    {/* </Button> */}
                </HStack>
            }

        </Flex>
    )
}
