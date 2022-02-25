import { atom, DefaultValue, selector, selectorFamily } from 'recoil';
import { FILE_TYPE } from '../utils/enums';
import { userState } from './Auth';

const jobsState = atom<Job[]>({
	key: 'jobsState',
	default: [],
});

export const jobsSelector = selector<Job[]>({
	key: 'jobs',
	get: ({ get }) => {
		const user = get(userState);
		if (user.authenticated) {
			return get(jobsState);
		}
		return [];
	},
	set: ({ set }, newJobs) => {
		if (newJobs instanceof DefaultValue) {
			return;
		}
		set(jobsState, () => newJobs);
	},
});

export const jobAtom = selectorFamily<Job, string>({
	key: 'job',
	get:
		(id) =>
		({ get }) => {
			const jobs = get(jobsState);
			return jobs.find((job) => job.id === id) as Job;
		},
});

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
