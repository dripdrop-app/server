import axios, { AxiosResponse } from 'axios';
import { atom } from 'jotai';
import { selectAtom, atomFamily, atomWithStorage } from 'jotai/utils';
import { FILE_TYPE } from '../utils/enums';
import { isBase64, isValidImage, isValidLink, isValidYTLink, resolveAlbumFromTitle } from '../utils/helpers';

const jobsState = atom<Job[]>([]);

export const jobsAtom = atom(
	(get) => get(jobsState),
	(get, set, update: Job[]) => {
		set(jobsState, update);
	}
);

export const jobAtom = atomFamily((jobID: string) => atom((get) => get(jobsState).find((job) => job.id === jobID)));

const initialFormState: MusicForm = {
	fileType: FILE_TYPE.YOUTUBE,
	youtubeUrl: '',
	filename: '',
	artworkUrl: '',
	title: '',
	artist: '',
	album: '',
	grouping: '',
};

export const musicFormAtom = atomWithStorage('musicForm', initialFormState, {
	getItem: (key) => {
		let form: MusicForm | string | null = localStorage.getItem(key);
		if (typeof form === 'string') {
			form = JSON.parse(form);
			form = form as MusicForm;
			form.filename = '';
			return form;
		}
		return initialFormState;
	},
	setItem: (key, form) => {
		return localStorage.setItem(key, JSON.stringify(form));
	},
	removeItem: (key) => {
		return localStorage.removeItem(key);
	},
});

export const validMusicForm = selectAtom(musicFormAtom, (form) => {
	const { fileType, youtubeUrl, filename, title, artist, album } = form;
	if (
		(fileType === FILE_TYPE.YOUTUBE &&
			youtubeUrl &&
			RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(youtubeUrl)) ||
		(fileType !== FILE_TYPE.YOUTUBE && filename)
	) {
		return !!title && !!artist && !!album;
	} else {
		return false;
	}
});

const variableMusicAtom = <T extends keyof MusicForm>(formKey: T) =>
	atom(
		(get) => get(musicFormAtom)[formKey],
		(get, set, update: MusicForm[T]) => {
			set(musicFormAtom, (form) => ({ ...form, [formKey]: update }));
		}
	);

export const titleAtom = atom(
	(get) => get(musicFormAtom).title,
	(get, set, update: string) => {
		set(musicFormAtom, (prev) => ({ ...prev, title: update }));
		set(albumAtom, resolveAlbumFromTitle(update));
	}
);

export const youtubeURLAtom = atom(
	(get) => get(musicFormAtom).youtubeUrl,
	async (get, set, update: string) => {
		const url = update;
		set(musicFormAtom, (prev) => ({ ...prev, youtubeUrl: url }));
		if (isValidYTLink(url)) {
			set(groupingLoadingAtom, true);
			try {
				const response: AxiosResponse<Pick<MusicForm, 'grouping'>> = await axios.get('/music/grouping', {
					params: { youtube_url: url },
				});
				set(groupingAtom, response.data.grouping);
			} finally {
				set(groupingLoadingAtom, false);
			}
		}
	}
);

export const artworkLoadingAtom = atom(false);

export const artworkURLAtom = atom(
	(get) => get(musicFormAtom).artworkUrl,
	async (get, set, update: string) => {
		const url = update;
		set(musicFormAtom, (prev) => ({ ...prev, artworkUrl: url }));
		if (url && !isValidImage(url) && !isBase64(url) && isValidLink(url)) {
			set(artworkLoadingAtom, true);
			try {
				const response: AxiosResponse<Pick<MusicForm, 'artworkUrl'>> = await axios.get('/music/artwork', {
					params: { artwork_url: url },
				});
				set(musicFormAtom, (prev) => ({ ...prev, artworkUrl: response.data.artworkUrl }));
			} finally {
				set(artworkLoadingAtom, false);
			}
		}
	}
);

export const validArtworkAtom = atom((get) => {
	const url = get(musicFormAtom).artworkUrl;
	return isBase64(url) || isValidImage(url);
});

export const fileTypeAtom = variableMusicAtom('fileType');

export const filenameAtom = variableMusicAtom('filename');

export const artistAtom = variableMusicAtom('artist');

export const albumAtom = variableMusicAtom('album');

export const groupingLoadingAtom = atom(false);

export const groupingAtom = variableMusicAtom('grouping');

export const tagsLoadingAtom = atom(false);
