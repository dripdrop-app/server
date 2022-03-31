import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { FILE_TYPE } from '../utils/enums';
import { isBase64, isValidImage, isValidYTLink, resolveAlbumFromTitle } from '../utils/helpers';

const initialState = {
	fileType: FILE_TYPE.YOUTUBE,
	youtubeUrl: '',
	filename: '',
	artworkUrl: '',
	title: '',
	artist: '',
	album: '',
	grouping: '',
	validYoutubeLink: false,
	validArtwork: false,
	valid: false,
};

export const musicSlice = createSlice({
	name: 'music',
	initialState,
	reducers: {
		updateForm: (state, action: PayloadAction<Partial<typeof initialState>>) => {
			if (action.payload.title && !state.album && !action.payload.album) {
				action.payload.album = resolveAlbumFromTitle(action.payload.title);
			}
			if (action.payload.youtubeUrl) {
				action.payload.validYoutubeLink = isValidYTLink(action.payload.youtubeUrl);
			}
			if (action.payload.artworkUrl !== undefined) {
				action.payload.validArtwork = isBase64(action.payload.artworkUrl) || isValidImage(action.payload.artworkUrl);
			}
			const newState = { ...state, ...action.payload };
			if (
				(newState.fileType === FILE_TYPE.YOUTUBE && newState.youtubeUrl && newState.validYoutubeLink) ||
				(newState.fileType !== FILE_TYPE.YOUTUBE && newState.filename)
			) {
				newState.valid = !!newState.title && !!newState.artist && !!newState.album;
			} else {
				newState.valid = false;
			}
			return newState;
		},
		resetForm: (state) => {
			return { ...initialState };
		},
	},
});

export const { updateForm, resetForm } = musicSlice.actions;
