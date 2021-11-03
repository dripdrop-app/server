import React, { createContext, useEffect, useState, useMemo, useCallback } from 'react';
import { FILE_TYPE } from '../utils/enums';
import { server_domain } from '../config';
import BlankImage from '../images/blank_image.jpeg';

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
	isValidArtwork: (url: string) => boolean;
	isBase64: (url: string) => boolean;
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
	isValidArtwork: () => false,
	isBase64: () => false,
});

const MusicContextProvider = (props: React.PropsWithChildren<any>) => {
	const [formInputs, setFormInputs] = useState<FormInputs>({ ...defaultFormData });
	const [validForm, setValidForm] = useState(false);
	const [jobs, setJobs] = useState<Job[]>([]);
	const [updatingForm, setUpdatingForm] = useState(false);
	const ws = useMemo(
		() => new WebSocket(`${process.env.NODE_ENV === 'production' ? 'wss' : 'ws'}://${server_domain}/ws/listenJobs`),
		[]
	);

	ws.onmessage = (event) => {
		const json = JSON.parse(event.data);
		const type = json.type;
		if (type === 'ALL') {
			setJobs([...json.jobs]);
		} else if (type === 'STARTED') {
			setJobs([...json.jobs, ...jobs]);
		} else if (type === 'COMPLETED') {
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
		}
	};

	const resetForm = useCallback(() => setFormInputs({ ...defaultFormData }), [setFormInputs]);

	const isBase64 = useCallback((url: string) => {
		const isBase64 = RegExp(/^data:image/).test(url);
		return isBase64;
	}, []);

	const isValidArtwork = useCallback(
		(url: string) => {
			const valid = RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);
			return valid || isBase64(url);
		},
		[isBase64]
	);

	const getArtwork = useCallback(async (url: string) => {
		const valid = RegExp(/^https:\/\/(www\.)?.+\.(jpg|jpeg|png)/).test(url);
		const isBase64 = RegExp(/^data:image/).test(url);
		if (url && valid && !isBase64) {
			const params = new URLSearchParams();
			params.append('artworkURL', url);
			const response = await fetch(`/getArtwork?${params}`);
			if (response.ok) {
				const json = await response.json();
				return json.artworkURL;
			}
		}
		return url;
	}, []);

	const getGrouping = useCallback(async (youTubeURL: string) => {
		const valid = RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(youTubeURL);
		if (youTubeURL && valid) {
			const params = new URLSearchParams();
			params.append('youtubeURL', youTubeURL);
			const response = await fetch(`/grouping?${params}`);
			if (response.ok) {
				const json = await response.json();
				return json.grouping;
			}
		}
		return youTubeURL;
	}, []);

	const updateFormInputs = useCallback(
		async (update: Partial<FormInputs>) => {
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
		},
		[formInputs, getArtwork, getGrouping, updatingForm]
	);

	const performOperation = useCallback(
		async (file?: File) => {
			const formData = new FormData();
			formData.append('youtubeURL', formInputs.youtubeURL || '');
			if (file) {
				formData.append('file', file);
			}
			if (formInputs.artworkURL) {
				formData.append('artworkURL', formInputs.artworkURL);
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
						formData.append('artworkURL', url);
					} catch {}
				}
			}
			formData.append('title', formInputs.title);
			formData.append('artist', formInputs.artist);
			formData.append('album', formInputs.album);
			formData.append('grouping', formInputs.grouping || '');
			const response = await fetch('/download', { method: 'POST', body: formData });
			if (response.ok) {
				resetForm();
			}
		},
		[formInputs, resetForm]
	);

	const removeJob = useCallback(
		async (deletedJobID: string) => {
			const params = new URLSearchParams();
			params.append('jobID', deletedJobID);
			const response = await fetch(`/deleteJob?${params}`);
			if (response.ok) {
				setJobs([...jobs.filter((job) => deletedJobID !== job.jobID)]);
			}
		},
		[jobs]
	);

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

	return (
		<MusicContext.Provider
			value={{
				formInputs,
				jobs,
				validForm,
				resetForm,
				updateFormInputs,
				performOperation,
				updatingForm,
				removeJob,
				isValidArtwork,
				isBase64,
			}}
		>
			{props.children}
		</MusicContext.Provider>
	);
};

export default MusicContextProvider;
