import { basicUrl } from "../api/api"

export const getData=()=>{
    const response = `${basicUrl}/api/data`
    return response
}

export const getSalesByRegion=()=>{
    const response = `${basicUrl}/sales-by-region`
    return response
}

export const getKPI=()=>{
    const response = `${basicUrl}/kpi`
    return response
}

export const getInsightsOfProduct=()=>{
    const response = `${basicUrl}/sales-by-product`
    return response
}

export const getAiInsights=()=>{
    const response = `${basicUrl}/ai-insights`
    return response
}
