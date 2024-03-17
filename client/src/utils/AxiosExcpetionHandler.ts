import toastHelper from './ToastHelper'

function handleException(toast: any, error: any){
    console.log(error.code);
    if (error.response && error.response.status !== 500){
        toastHelper.makeToast(
            toast,
            error.response.data.error,
            'warning'
        )
    }
    else{
        console.log('ok')
        toastHelper.makeToast(
            toast,
            "Oops! Something went wrong. Please try again.",
            'error'
        )
    }
    console.error('Error in the saving request:', error.message)
}

export default {
    handleException
}
  