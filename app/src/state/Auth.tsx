import { atom } from 'recoil';
import axios, { AxiosResponse } from 'axios';

const checkSession = async () => {
	try {
		const response: AxiosResponse<User> = await axios.get('/auth/session');
		return { ...response.data, authenticated: true };
	} catch {
		return initialUserState;
	}
};

export const initialUserState: UserState = {
	email: '',
	admin: false,
	authenticated: false,
};

export const userState = atom<UserState>({
	key: 'auth',
	default: checkSession(),
});
