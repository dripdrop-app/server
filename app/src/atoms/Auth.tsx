import { atom } from 'recoil';
import axios, { AxiosResponse } from 'axios';

export const userAtom = atom({
	key: 'user',
	default: (async () => {
		try {
			const response: AxiosResponse<User> = await axios.get('/auth/check_session');
			return response.data;
		} catch {}
		return null;
	})(),
});
