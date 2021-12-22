export {};

declare global {
	interface FetchResponse<T> {
		data: T;
		success: boolean;
		error: boolean;
	}

	interface User {
		email: string;
		admin: boolean;
	}
}
