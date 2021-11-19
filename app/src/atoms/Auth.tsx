import { atom } from 'recoil';
import { customFetch } from '../utils/helpers';

export const userAtom = atom({
	key: 'user',
	default: (async () => {
		const response = await customFetch<User | null>('/auth/checkSession');
		if (response.success) {
			return response.data;
		}
		return null;
	})(),
});
