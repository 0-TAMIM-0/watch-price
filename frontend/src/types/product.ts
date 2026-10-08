export interface PriceHistory {
    id: number
    product_id: number
    price: number
    checked_at: string
}

export interface Product {
    id?: number
    name: string
    category: string | null
    image_url: string | null
    target_price: number
    current_price: number
    created_at?: string
    target_reached?: boolean

    price_history?: PriceHistory[]
}
