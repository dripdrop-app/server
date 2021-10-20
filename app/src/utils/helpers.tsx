export const debounce = (callback: (...args: any[]) => {}, timeout: number) => {
	let timer: NodeJS.Timeout;
	return (...args: any[]) => {
		clearTimeout(timer);
		timer = setTimeout(() => callback(...args), timeout);
	};
};
