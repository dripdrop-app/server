import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { FILE_TYPE } from '../utils/enums';
import { isBase64, isValidImage, isValidYTLink, resolveAlbumFromTitle } from '../utils/helpers';

const initialFormState = {
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
	initialState: {
		form: initialFormState,
	},
	reducers: {
		updateForm: (state, action: PayloadAction<Partial<typeof initialFormState>>) => {
			const form = state.form;
			if (action.payload.title && !form.album && !action.payload.album) {
				action.payload.album = resolveAlbumFromTitle(action.payload.title);
			}
			if (action.payload.youtubeUrl) {
				action.payload.validYoutubeLink = isValidYTLink(action.payload.youtubeUrl);
			}
			if (action.payload.artworkUrl !== undefined) {
				action.payload.validArtwork = isBase64(action.payload.artworkUrl) || isValidImage(action.payload.artworkUrl);
			}
			const newFormState = { ...form, ...action.payload };
			if (
				(newFormState.fileType === FILE_TYPE.YOUTUBE && newFormState.youtubeUrl && newFormState.validYoutubeLink) ||
				(newFormState.fileType !== FILE_TYPE.YOUTUBE && newFormState.filename)
			) {
				newFormState.valid = !!newFormState.title && !!newFormState.artist && !!newFormState.album;
			} else {
				newFormState.valid = false;
			}
			state.form = { ...newFormState };
		},
		resetForm: (state) => {
			return { ...state, form: initialFormState };
		},
	},
});

export const { updateForm, resetForm } = musicSlice.actions;
