export default class Sensor {
    category: string;
    description: string;
    internalName: string;
    isHeadMounted: boolean;
    name: string;
    thresholdHigh: null | number;
    thresholdLow: null | number;
    type: string;
    unit: string;

    constructor(data: any) {
      this.category = data.category;
      this.description = data.description;
      this.internalName = data.internalName;
      this.isHeadMounted = data.isHeadMounted;
      this.name = data.name;
      this.thresholdHigh = data.thresholdHigh;
      this.thresholdLow = data.thresholdLow;
      this.type = data.type;
      this.unit = data.unit;
  }
}