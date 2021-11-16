import React, { useCallback, useContext, useEffect, useMemo, useRef } from 'react';
import { Typography, Divider, Stack, CircularProgress } from '@mui/material';
import { MusicContext } from '../../context/Music';
import FileSelector from './FileSelector';
import ArtworkInput from './ArtworkInput';
import TagInputs from './TagInputs';
import FormActions from './FormActions';
import useLazyFetch from '../../hooks/useLazyFetch';
import BlankImage from '../../images/blank_image.jpeg';

const MusicForm = () => {
	const { formInputs, resetForm } = useContext(MusicContext);
	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	const { youtube_url, artwork_url, title, artist, album, grouping } = formInputs;

	const [performOperation, performOperationStatus] = useLazyFetch();

	const run = useCallback(async () => {
		const formData = new FormData();
		if (fileInputRef.current && fileInputRef.current.files && fileInputRef.current.files.length > 0) {
			const file = fileInputRef.current.files[0];
			formData.append('file', file);
		}
		formData.append('youtube_url', youtube_url || '');
		if (artwork_url) {
			formData.append('artwork_url', artwork_url);
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
		formData.append('title', title);
		formData.append('artist', artist);
		formData.append('album', album);
		formData.append('grouping', grouping || '');
		performOperation('/music/download', { method: 'POST', body: formData });
	}, [album, artist, artwork_url, grouping, performOperation, title, youtube_url]);

	useEffect(() => {
		if (performOperationStatus.isSuccess) {
			resetForm();
		}
	}, [performOperationStatus.isSuccess, resetForm]);

	return useMemo(
		() => (
			<React.Fragment>
				<Typography sx={{ my: 5 }} variant="h2">
					MP3 Downloader / Converter
				</Typography>
				<Divider variant="middle" />
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={0.5} sx={{ my: 10 }}>
					<FileSelector fileInputRef={fileInputRef} />
				</Stack>
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={1} sx={{ my: 10 }}>
					<ArtworkInput />
				</Stack>
				<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={0.5} sx={{ my: 10 }}>
					<TagInputs />
				</Stack>
				<Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ my: 10 }}>
					{performOperationStatus.isLoading ? <CircularProgress /> : <FormActions run={run} />}
				</Stack>
			</React.Fragment>
		),
		[performOperationStatus.isLoading, run]
	);
};

export default MusicForm;
