import { useReducer, useState } from 'react'
import SidebarStatusReducer from './utils/reducers/SidebarStatusReducer'
import { BrowserRouter } from 'react-router-dom'
import SidebarStatusContext from './utils/contexts/SidebarStatusContext'
import { ChakraProvider, useToast} from '@chakra-ui/react'
import ConfigurationContext from './utils/contexts/ConfigurationContext'
import Configuration from './models/Configuration'  
import Layout from './layout/Layout'
import './App.css';

function App() {
    const [sidebarStatus, dispatchSidebarStatus] = useReducer(SidebarStatusReducer, {
    type: 'sidebar',
    status: 'open',
    previousType: 'sidebar',
    previousStatus: 'open'
    })

    const valueSidebarStatus = { sidebarStatus, dispatchSidebar: dispatchSidebarStatus }

    const [configuration, setConfiguration] = useState<Configuration>(new Configuration());
    const toast = useToast();
    const [isSaved, setIsSaved] = useState(true);
    const contextValue = {
        configuration : configuration,
        setConfiguration: setConfiguration,
        isSaved: isSaved,
        setIsSaved: setIsSaved,
        toast: toast
  };

    return (        
        <ConfigurationContext.Provider value={contextValue}>
            <BrowserRouter>
                <ChakraProvider>
                    <SidebarStatusContext.Provider value={valueSidebarStatus}>
                        <Layout/>
                    </SidebarStatusContext.Provider>
                 </ChakraProvider>
            </BrowserRouter>
        </ConfigurationContext.Provider>
    );
}

export default App;
