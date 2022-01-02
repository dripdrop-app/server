import { atom } from 'recoil';
import { customFetch } from '../utils/helpers';

export const initialState = {
	email: '',
};

export const youtubeAuthAtom = atom<YoutubeState>({
	key: 'youtubeAuth',
	default: (async () => {
		const response = await customFetch<YoutubeState, null>('/youtube/account');
		if (response.success) {
			return response.data;
		}
		return initialState;
	})(),
});

export const youtubeUserVideosAtom = atom({
	key: 'youtubeUserVideos',
	default: async () => {
		const response = await customFetch('/youtube/videos');
		if (response.success) {
			return response.data;
		}
		return initialState;
	},
});
