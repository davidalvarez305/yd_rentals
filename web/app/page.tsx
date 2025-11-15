'use client'
import { useState } from "react";

export default function Home() {
	const [count, setCount] = useState(0);

	function handleIncrementCount() {
		setCount(prev => prev += 1);
	}

	function handleDecrementCount() {
		setCount(prev => prev -= 1);
	}

	return (
		<div>
			<h1>Home</h1>
			<h1>{count}</h1>
			<button onClick={() => handleIncrementCount()}>+</button>
			<button onClick={() => handleDecrementCount()}>-</button>
		</div>
	)
}
