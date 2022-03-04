import { atom, selector } from 'recoil';
import axios, { AxiosResponse } from 'axios';

const initialUserState: UserState = {
	email: '',
	admin: false,
	authenticated: false,
};

const checkSession = async () => {
	try {
		const response: AxiosResponse<User> = await axios.get('/auth/session');
		return { ...response.data, authenticated: true };
	} catch {
		return initialUserState;
	}
};

export const userState = atom<UserState>({
	key: 'auth',
	default: checkSession(),
});

export const resetUserState = selector({
	key: 'resetAuth',
	get: () => null,
	set: ({ set }) => set(userState, initialUserState),
});
