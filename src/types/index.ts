// src/types/index.ts
// Domain Types and Interfaces for Enterprise Online Cosmetic Store Platform (ARCH-5134)

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  shade: string;
  skin_tone: string;
  undertone: string;
  finish: string;
  formulation: string[];
  allergens: string[];
  ingredients?: string;
  fda_mocra_listed?: boolean;
  eu_1223_2009_compliant?: boolean;
  image_url?: string;
}

export interface InventoryItem {
  product_id: string;
  available_stock: number;
  reserved_stock: number;
}

export interface ReservationRequest {
  session_id: string;
  items: Array<{
    product_id: string;
    quantity: number;
  }>;
}

export interface ReservationResponse {
  reservation_id: string;
  status: 'ACTIVE' | 'EXPIRED' | 'CONVERTED';
  expires_at: string;
}

export interface Promotion {
  code: string;
  description: string;
  discount_type: 'PERCENTAGE' | 'FIXED_AMOUNT' | 'SHADE_BUNDLE';
  discount_value: number;
  minimum_cart_value: number;
  is_active: boolean;
}

export interface ShippingAddress {
  full_name: string;
  address_line1: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface CheckoutRequest {
  reservation_id?: string;
  email: string;
  customer_name?: string;
  is_guest?: boolean;
  shipping_address: ShippingAddress;
  payment_method: string;
  items: Array<{
    product_id: string;
    quantity: number;
    price: number;
  }>;
  promo_code?: string;
}

export interface Order {
  id: string;
  email: string;
  customer_name: string;
  is_guest: boolean;
  total_amount: number;
  discount_amount: number;
  promo_code?: string;
  status: string;
  tracking_number: string;
  carrier: string;
  shipping_address: ShippingAddress;
  created_at: string;
  items?: Array<{
    product_id: string;
    quantity: number;
    unit_price: number;
  }>;
}

export interface ReturnRequest {
  order_id: string;
  type: 'RETURN' | 'SHADE_EXCHANGE';
  product_id: string;
  target_shade_id?: string;
  reason: string;
}

export interface Webhook3PLPayload {
  event: string;
  tracking_number: string;
  order_id: string;
  carrier?: string;
  status: string;
}

export interface RFC7807ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  invalid_params?: Array<{ name: string; reason: string }>;
}
