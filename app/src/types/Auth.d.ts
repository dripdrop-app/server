export {};

declare global {
	type FetchResponse<SuccessResponse, FailedResponse> =
		| {
				data: SuccessResponse;
				success: true;
				error: false;
		  }
		| {
				data: FailedResponse;
				success: false;
				error: true;
		  };

	interface User {
		email: string;
		admin: boolean;
	}
}
