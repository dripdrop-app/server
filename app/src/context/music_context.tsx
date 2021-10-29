import React, { createContext, useEffect, useState, useMemo, useCallback } from 'react';
import { FILE_TYPE } from '../utils/enums';

interface BaseInputs {
	youtubeURL: string | null;
	filename: string | null;
	artworkURL: string | null;
	title: string;
	artist: string;
	album: string;
	grouping: string | null;
}

export interface Job extends BaseInputs {
	jobID: string;
	completed: boolean;
	failed: boolean;
}

interface FormInputs extends BaseInputs {
	fileType: keyof typeof FILE_TYPE;
}

interface MusicContextValue {
	jobs: Job[];
	formInputs: FormInputs;
	validForm: boolean;
	resetForm: () => void;
	updateFormInputs: (update: Partial<FormInputs>) => void;
	performOperation: (file?: File) => void;
	updatingForm: boolean;
	removeJob: (jobID: string) => void;
}

const defaultFormData = {
	fileType: FILE_TYPE.YOUTUBE,
	youtubeURL: '',
	filename: '',
	artworkURL: '',
	title: '',
	artist: '',
	album: '',
	grouping: '',
};

export const MusicContext = createContext<MusicContextValue>({
	formInputs: {
		...defaultFormData,
	},
	validForm: false,
	jobs: [],
	resetForm: () => {},
	updateFormInputs: () => {},
	performOperation: () => {},
	updatingForm: false,
	removeJob: () => {},
});

const MusicContextProvider = (props: React.PropsWithChildren<any>) => {
	const [formInputs, setFormInputs] = useState<FormInputs>({ ...defaultFormData });
	const [validForm, setValidForm] = useState(false);
	const [jobs, setJobs] = useState<Job[]>([]);
	const [updatingForm, setUpdatingForm] = useState(false);
	const ws = useMemo(() => new WebSocket(`ws://localhost:5000/listenJobs`), []);

	ws.onmessage = (event) => {
		const json = JSON.parse(event.data);
		const completedJobs = json.jobs.reduce((map: any, job: Job) => {
			map[job.jobID] = job;
			return map;
		}, {});
		jobs.forEach((job, index) => {
			if (completedJobs[job.jobID]) {
				jobs[index] = completedJobs[job.jobID];
			}
		});
		setJobs([...jobs]);
	};

	const resetForm = () => setFormInputs({ ...defaultFormData });

	const getArtwork = async (url: string) => {
		const valid = RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);
		if (url && !valid) {
			const params = new URLSearchParams();
			params.append('artworkURL', url);
			const response = await fetch(`/getArtwork?${params}`);
			if (response.status === 200) {
				const json = await response.json();
				return json.artworkURL;
			}
		}
		return url;
	};

	const getGrouping = async (youTubeURL: string) => {
		const valid = RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(youTubeURL);
		if (youTubeURL && valid) {
			const params = new URLSearchParams();
			params.append('youtubeURL', youTubeURL);
			const response = await fetch(`/grouping?${params}`);
			if (response.status === 200) {
				const json = await response.json();
				return json.grouping;
			}
		}
		return youTubeURL;
	};

	const updateFormInputs = async (update: Partial<FormInputs>) => {
		if (!updatingForm) {
			setUpdatingForm(true);
			if (update.fileType) {
				if (update.fileType === FILE_TYPE.YOUTUBE) {
					update.filename = '';
				} else if (update.fileType === FILE_TYPE.MP3_UPLOAD || update.fileType === FILE_TYPE.WAV_UPLOAD) {
					update.youtubeURL = '';
				}
			}
			if (update.filename?.endsWith('.mp3')) {
				update.fileType = FILE_TYPE.MP3_UPLOAD;
			} else if (update.filename?.endsWith('.wav')) {
				update.fileType = FILE_TYPE.WAV_UPLOAD;
			}
			if (update.title && !update.album) {
				const text = update.title;
				update.album = '';

				const openPar = text.indexOf('(');
				const closePar = text.indexOf(')');
				const specialTitle = (openPar !== -1 || closePar !== -1) && openPar < closePar;

				const songTitle = specialTitle ? text.substring(0, openPar).trim() : text.trim();
				update.album = songTitle;
				const songTitleWords = songTitle.split(' ');

				if (songTitleWords.length > 2) {
					update.album = songTitleWords.map((word) => word.charAt(0)).join('');
				}
				if (specialTitle) {
					const specialWords = text.substring(openPar + 1, closePar).split(' ');
					update.album = `${update.album} - ${specialWords[specialWords.length - 1]}`;
				} else {
					update.album = update.album ? `${update.album} - Single` : '';
				}
			}
			if (update.artworkURL) {
				update.artworkURL = await getArtwork(update.artworkURL);
			}
			if (update.youtubeURL && !update.grouping) {
				update.grouping = await getGrouping(update.youtubeURL);
			}
			Object.keys(formInputs).forEach((key) => {
				const dataKey = key as keyof FormInputs;
				if (update[dataKey] === undefined || update[dataKey] === null) {
					if (dataKey === 'fileType') {
						update[dataKey] = formInputs.fileType;
					} else {
						update[dataKey] = formInputs[dataKey] || '';
					}
				}
			});

			setFormInputs({ ...(update as FormInputs) });
			setUpdatingForm(false);
		}
	};

	const performOperation = async (file?: File) => {
		const formData = new FormData();
		formData.append('youtubeURL', formInputs.youtubeURL || '');
		if (file) {
			formData.append('file', file);
		}
		formData.append('artworkURL', formInputs.artworkURL || '');
		formData.append('title', formInputs.title);
		formData.append('artist', formInputs.artist);
		formData.append('album', formInputs.album);
		formData.append('grouping', formInputs.grouping || '');
		const response = await fetch('/download', { method: 'POST', body: formData });
		if (response.status === 200) {
			const json = await response.json();
			const job = json.job;
			setJobs([job, ...jobs]);
			resetForm();
		}
	};

	const removeJob = async (deletedJobID: string) => {
		const params = new URLSearchParams();
		params.append('jobID', deletedJobID);
		const response = await fetch(`/deleteJob?${params}`);
		if (response.status === 200) {
			setJobs([...jobs.filter((job) => deletedJobID !== job.jobID)]);
		}
	};

	const getJobs = async () => {
		const response = await fetch('/getJobs');
		if (response.status === 200) {
			const json = await response.json();
			const jobs = json.jobs;
			setJobs([...jobs]);
		}
	};

	useEffect(() => {
		if (
			(formInputs.youtubeURL && RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(formInputs.youtubeURL)) ||
			formInputs.filename
		) {
			setValidForm(!!formInputs.title && !!formInputs.artist && !!formInputs.album);
		} else {
			setValidForm(false);
		}
	}, [formInputs]);

	useEffect(() => {
		const jobIDs = jobs.filter((job) => !job.completed).map((job) => job.jobID);
		if (ws.readyState === 1) {
			ws.send(JSON.stringify({ jobIDs: jobIDs }));
		}
	}, [jobs, ws]);

	useEffect(() => {
		getJobs();

		return () => ws.close();
	}, [ws]);

	return (
		<MusicContext.Provider
			value={{ formInputs, jobs, validForm, resetForm, updateFormInputs, performOperation, updatingForm, removeJob }}
		>
			{props.children}
		</MusicContext.Provider>
	);
};

export default MusicContextProvider;
