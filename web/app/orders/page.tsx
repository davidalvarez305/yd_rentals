'use client'

import { Fragment, useCallback, useEffect, useState } from "react"
import { ORDERS_ENDPOINT } from "../constants";

export default function Orders() {
    const [orders, setOrders] = useState([]);

    const handleGetOrders = useCallback(() => {
        fetch(ORDERS_ENDPOINT)
            .then(response => {
                if (response.ok) {
                    return response.json()
                }
            })
            .then(data => {
                setOrders(data.data);
            });
    }, []);

    useEffect(() => handleGetOrders(), [handleGetOrders]);

    return (
        <Fragment>
            {orders.map(order => (
                <p>{order.external_id}</p>
            ))}
        </Fragment>
    )
}