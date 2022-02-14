import { atom, DefaultValue, selector, selectorFamily } from 'recoil';
import { FILE_TYPE } from '../utils/enums';

export const initialFormState: MusicForm = {
	fileType: FILE_TYPE.YOUTUBE,
	youtubeUrl: '',
	filename: '',
	artworkUrl: '',
	title: '',
	artist: '',
	album: '',
	grouping: '',
	groupingLoading: false,
	tagsLoading: false,
};

export const musicFormAtom = atom<MusicForm>({
	key: 'musicForm',
	default: { ...initialFormState },
});

export const jobsAtom = atom<Job[]>({
	key: 'jobs',
	default: [],
});

export const jobAtom = selectorFamily<Job, string>({
	key: 'job',
	get:
		(id) =>
		({ get }) =>
			get(jobsAtom).find((job) => job.id === id) as Job,
});

const variableFormSelector = <T extends keyof MusicForm>(formKey: keyof MusicForm) =>
	selector<MusicForm[T]>({
		key: formKey,
		get: ({ get }) => get(musicFormAtom)[formKey] as MusicForm[T],
		set: ({ set }, newFormValue) => {
			if (newFormValue instanceof DefaultValue) {
				return;
			}
			set(musicFormAtom, (prev) => ({ ...prev, [formKey]: newFormValue }));
		},
	});

export const titleSelector = variableFormSelector<'title'>('title');

export const youtubeURLSelector = variableFormSelector<'youtubeUrl'>('youtubeUrl');

export const artworkURLSelector = variableFormSelector<'artworkUrl'>('artworkUrl');

export const fileTypeSelector = variableFormSelector<'fileType'>('fileType');

export const filenameSelector = variableFormSelector<'filename'>('filename');

export const artistSelector = variableFormSelector<'artist'>('artist');

export const albumSelector = variableFormSelector<'album'>('album');

export const groupingSelector = variableFormSelector<'grouping'>('grouping');

export const groupingLoadingSelector = variableFormSelector<'groupingLoading'>('groupingLoading');

export const tagsLoadingSelector = variableFormSelector<'tagsLoading'>('tagsLoading');
