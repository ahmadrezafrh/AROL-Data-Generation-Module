import { createContext, SetStateAction, Dispatch } from 'react';
import Configuration from '../../models/Configuration'  


interface ConfigurationContextProps {
    configuration: Configuration;
    setConfiguration: Dispatch<SetStateAction<Configuration>>;
    isSaved: boolean;
    setIsSaved: Dispatch<SetStateAction<boolean>>;
    toast : any
}

const ConfigurationContext = createContext<ConfigurationContextProps>({
    configuration: new Configuration(),
    setConfiguration: () => {},
    isSaved: true,
    setIsSaved: () => {},
    toast: null
});


export default ConfigurationContext;