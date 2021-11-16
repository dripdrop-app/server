import React, { useCallback, useContext, useEffect, useMemo } from 'react';
import { Button, Switch, TextField } from '@mui/material';
import { MusicContext } from '../../context/Music';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps } from '../../utils/helpers';
import YoutubeURLInput from './YoutubeURLInput';
import useLazyFetch from '../../hooks/useLazyFetch';

interface FileSwitchProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FileSwitch = (props: FileSwitchProps) => {
	const { updateFormInputs, formInputs } = useContext(MusicContext);
	const { fileType, filename } = formInputs;
	const { fileInputRef } = props;

	const [getFileTags, getFileTagsStatus] = useLazyFetch();

	const onFileSwitchChange = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
			if (checked) {
				updateFormInputs({ fileType: FILE_TYPE.WAV_UPLOAD, filename: '', youtube_url: '' });
			} else {
				if (fileInputRef.current && fileInputRef.current.files) {
					fileInputRef.current.files = null;
				}
				updateFormInputs({ fileType: FILE_TYPE.YOUTUBE, filename: '', youtube_url: '' });
			}
		},
		[fileInputRef, updateFormInputs]
	);

	const onBrowseClick = useCallback(() => {
		if (fileType !== FILE_TYPE.YOUTUBE) {
			if (fileInputRef.current) {
				fileInputRef.current.click();
			}
		}
	}, [fileInputRef, fileType]);

	const onFileChange = useCallback(
		async (event: React.ChangeEvent<HTMLInputElement>) => {
			const files = event.target.files;
			if (files && files.length > 0) {
				const file = files[0];
				const formData = new FormData();
				formData.append('file', file);
				updateFormInputs({ filename: file.name });
				getFileTags('/music/getTags', { method: 'POST', body: formData });
			}
		},
		[getFileTags, updateFormInputs]
	);

	useEffect(() => {
		if (getFileTagsStatus.isSuccess) {
			const { title, artist, album, grouping, artwork_url } = getFileTagsStatus.data;
			updateFormInputs({
				title: title || '',
				artist: artist || '',
				album: album || '',
				grouping: grouping || '',
				artwork_url: artwork_url || '',
			});
		}
	}, [getFileTagsStatus.data, getFileTagsStatus.isSuccess, updateFormInputs]);

	return useMemo(
		() => (
			<React.Fragment>
				<YoutubeURLInput />
				<Switch
					onChange={onFileSwitchChange}
					value={fileType !== FILE_TYPE.YOUTUBE}
					checked={fileType !== FILE_TYPE.YOUTUBE}
				/>
				<TextField
					{...defaultTextFieldProps}
					onClick={onBrowseClick}
					value={filename}
					label="File Upload"
					disabled
					required
					error={filename === '' && fileType !== FILE_TYPE.YOUTUBE}
				/>
				<input ref={fileInputRef} onChange={onFileChange} style={{ display: 'none' }} type="file" accept=".mp3,.wav" />
				<Button
					variant="contained"
					disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
					onClick={onBrowseClick}
				>
					Browse
				</Button>
			</React.Fragment>
		),
		[fileInputRef, fileType, filename, onBrowseClick, onFileChange, onFileSwitchChange]
	);
};

export default FileSwitch;
