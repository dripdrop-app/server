import { atom } from 'jotai';
import axios, { AxiosResponse } from 'axios';

const initialUserState: UserState = {
	email: '',
	admin: false,
	authenticated: false,
};

const userAtom = atom({ loading: true, data: initialUserState });

export const userAtomState = atom(
	(get) => get(userAtom),
	(get, set, update: UserState | undefined) => {
		if (update) {
			return set(userAtom, { loading: false, data: update });
		}
		const checkSession = async () => {
			set(userAtom, (prev) => ({ ...prev, loading: true }));
			try {
				const response: AxiosResponse<User> = await axios.get('/auth/session');
				set(userAtom, { loading: false, data: { ...response.data, authenticated: true } });
			} catch {
				set(userAtom, { loading: false, data: initialUserState });
			}
		};
		checkSession();
	}
);

userAtomState.onMount = (setAtom) => setAtom();

export const resetUserState = atom(null, (get, set, update) => {
	set(userAtom, { loading: false, data: initialUserState });
});
