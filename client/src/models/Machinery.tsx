export default class Machinery {
    uid: string
    modelID: string
    modelName: string
    modelType: string
    numHeads: number

    constructor(data: any) {
        this.uid = data.uid;
        this.modelID = data.modelID;
        this.modelName = data.modelName;
        this.modelType = data.modelType;
        this.numHeads = data.numHeads;
    }
}
