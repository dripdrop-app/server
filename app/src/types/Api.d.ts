interface ValidationError {
	loc: string[];
	msg: string;
	type: string;
}

interface ErrorResponse {
	detail: ValidationError[] | string;
}
