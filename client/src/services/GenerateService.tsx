import { AxiosResponse } from 'axios'
import AxiosInstance from '../utils/AxiosInstance'

async function insertConfiguration(configuration: any): Promise<AxiosResponse<any>> {
    try {   
        const response = await AxiosInstance.post('/generate/configuration', configuration, { 
            headers: {
                'Content-Type': 'application/json'
            }
        })
        return response
    } 
    catch (error: any) {
        throw error 
    }
}

async function updateConfiguration(name: any, machineriesSelected: any): Promise<AxiosResponse<any>>  {
    try {  
        const response = await AxiosInstance.put(`/generate/configuration/${name}`, machineriesSelected, { 
            headers: {
                'Content-Type': 'application/json'
            }
        })

        return response
    } 
    catch (error: any) {
        if (error.response && error.response.status === 404) {
            return error.response 
        } 
        else {
            throw error
        }
    }
}

async function getConfiguration(name: any): Promise<AxiosResponse<any>>  {
    try {  
        const response = await AxiosInstance.get(`/generate/configurations/${name}`)

        return response
    } 
    catch (error: any) {
        if (error.response && error.response.status === 404) {
            return error.response 
        } 
        else {
            console.error(`Error during the file JSON sending: ${error.message}`, 'Response:', error.response?.data)
            throw error
        }
    }
}

async function getConfigurationsNames(): Promise<AxiosResponse<any>>  {
    try {  
        const response = await AxiosInstance.get('/generate/configuration/names')

        return response
    } 
    catch (error:any) {
        throw error 
    }
}

async function deleteConfiguration(name: string): Promise<AxiosResponse<any>> {
    try {   
        const response = await AxiosInstance.delete(`/generate/configuration/${name}`)

        return response
    } catch (error:any) {
        throw error 
    }
}

async function statusModel(): Promise<AxiosResponse<any>>  {
    try { 
        const response = await AxiosInstance.get('/generate/model/status')
    
        return response
    } 
    catch (error:any) {
        throw error 
    }
}

async function trainModel(): Promise<AxiosResponse<any>>  {
    try { 
        const response = await AxiosInstance.put('/generate/model/train')
    
        return response
    } 
    catch (error:any) {
        throw error 
    }
}

async function runSimulation(configuration: any): Promise<AxiosResponse<any>> {
    try { 
        const response = await AxiosInstance.post('/generate/simulation/run', configuration, { 
        headers: {
            'Content-Type': 'application/json'
            }
        })
        return response
    } 
    catch (error: any) {
        throw error
    }
}

async function stopSimulation(): Promise<AxiosResponse<any>>  {
    try { 
        const response = await AxiosInstance.put('/generate/simulation/stop')

    return response
    }  
    catch (error:any) {
        throw error 
    }
}


export default {
    insertConfiguration,
    updateConfiguration,
    getConfiguration,
    deleteConfiguration,
    getConfigurationsNames,
    statusModel,
    trainModel,
    runSimulation,
    stopSimulation
}

