import React, { useEffect, useState } from 'react';

export const useDebounce = (value: any, timeout: number) => {
	const [debounceValue, setDebouncedValue] = useState(value);

	useEffect(() => {
		const handler = setTimeout(() => setDebouncedValue(value), timeout);
		return () => {
			clearTimeout(handler);
		};
	}, [timeout, value]);

	return debounceValue;
};


// export const useSmartContext = <T>(selector: () => {}) => {
// 	const [partialContext, updatePartialContext] = useState(selector());
// }