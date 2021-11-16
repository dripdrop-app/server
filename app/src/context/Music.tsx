import React, { createContext, useEffect, useState, useCallback, useReducer } from 'react';
import { FILE_TYPE } from '../utils/enums';
import BlankImage from '../images/blank_image.jpeg';
import useWebsocket from '../hooks/useWebsocket';

interface BaseInputs {
	youtube_url: string | null;
	filename: string | null;
	artwork_url: string | null;
	title: string;
	artist: string;
	album: string;
	grouping: string | null;
}

export interface Job extends BaseInputs {
	job_id: string;
	completed: boolean;
	failed: boolean;
}

export interface FormInputs extends BaseInputs {
	fileType: keyof typeof FILE_TYPE;
}

interface MusicContextValue {
	jobs: Job[];
	formInputs: FormInputs;
	validForm: boolean;
	resetForm: () => void;
	updateFormInputs: (update: Partial<FormInputs>) => void;
	performOperation: (file?: File) => Promise<void>;
	removeJob: (jobID: string) => void;
}

const initialFormState: FormInputs = {
	fileType: FILE_TYPE.YOUTUBE,
	youtube_url: '',
	filename: '',
	artwork_url: '',
	title: '',
	artist: '',
	album: '',
	grouping: '',
};

type Action = { type: 'UPDATE'; payload: Partial<BaseInputs> };

const reducer = (state = initialFormState, action: Action): FormInputs => {
	if (action.type === 'UPDATE') {
		return { ...state, ...action.payload };
	}
	return state;
};

export const MusicContext = createContext<MusicContextValue>({
	formInputs: {} as FormInputs,
	validForm: false,
	jobs: [],
	resetForm: () => {},
	updateFormInputs: () => {},
	performOperation: () => Promise.resolve(),
	removeJob: () => {},
});

const MusicContextProvider = (props: React.PropsWithChildren<{}>) => {
	const [formInputs, dispatch] = useReducer(reducer, initialFormState);
	const [validForm, setValidForm] = useState(false);
	const [jobs, setJobs] = useState<Job[]>([]);

	const socketHandler = useCallback(
		(event) => {
			const json = JSON.parse(event.data);
			const type = json.type;
			if (type === 'ALL') {
				setJobs([...json.jobs]);
			} else if (type === 'STARTED') {
				setJobs([...json.jobs, ...jobs]);
			} else if (type === 'COMPLETED') {
				const completedJobs = json.jobs.reduce((map: any, job: any) => {
					map[job.job_id] = job;
					return map;
				}, {});
				jobs.forEach((job, index) => {
					if (completedJobs[job.job_id]) {
						jobs[index] = completedJobs[job.job_id];
					}
				});
				setJobs([...jobs]);
			}
		},
		[jobs]
	);

	useWebsocket('/music/listenJobs', socketHandler);

	const resetForm = useCallback(() => dispatch({ type: 'UPDATE', payload: initialFormState }), []);

	const updateFormInputs = useCallback(
		(update: Partial<FormInputs>) => dispatch({ type: 'UPDATE', payload: update }),
		[]
	);

	const performOperation = useCallback(
		async (file?: File) => {
			const formData = new FormData();
			formData.append('youtube_url', formInputs.youtube_url || '');
			if (file) {
				formData.append('file', file);
			}
			if (formInputs.artwork_url) {
				formData.append('artwork_url', formInputs.artwork_url);
			} else {
				const imageResponse = await fetch(BlankImage);
				if (imageResponse.ok) {
					const blob = await imageResponse.blob();
					try {
						const readFilePromise = () =>
							new Promise((resolve, reject) => {
								const reader = new FileReader();
								reader.onloadend = () => resolve(reader.result);
								reader.onerror = reject;
								reader.readAsDataURL(blob);
							});
						const url = (await readFilePromise()) as string;
						formData.append('artwork_url', url);
					} catch {}
				}
			}
			formData.append('title', formInputs.title);
			formData.append('artist', formInputs.artist);
			formData.append('album', formInputs.album);
			formData.append('grouping', formInputs.grouping || '');
			const response = await fetch('/music/download', { method: 'POST', body: formData });
			if (response.ok) {
				resetForm();
			}
		},
		[formInputs, resetForm]
	);

	const removeJob = useCallback(
		async (deletedJobID: string) => {
			const params = new URLSearchParams();
			params.append('job_id', deletedJobID);
			const response = await fetch(`/music/deleteJob?${params}`);
			if (response.ok) {
				setJobs([...jobs.filter((job) => deletedJobID !== job.job_id)]);
			}
		},
		[jobs]
	);

	useEffect(() => {
		if (
			(formInputs.youtube_url && RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(formInputs.youtube_url)) ||
			formInputs.filename
		) {
			setValidForm(!!formInputs.title && !!formInputs.artist && !!formInputs.album);
		} else {
			setValidForm(false);
		}
	}, [formInputs]);

	return (
		<MusicContext.Provider
			value={{
				formInputs,
				jobs,
				validForm,
				resetForm,
				updateFormInputs,
				performOperation,
				removeJob,
			}}
		>
			{props.children}
		</MusicContext.Provider>
	);
};

export default MusicContextProvider;
