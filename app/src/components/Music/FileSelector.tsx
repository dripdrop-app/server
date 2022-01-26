import React, { useCallback, useEffect, useMemo } from 'react';
import { Button, Switch, TextField } from '@mui/material';
import { filenameSelector, fileTypeSelector, musicFormAtom, tagsLoadingSelector } from '../../atoms/Music';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps, resolveAlbumFromTitle } from '../../utils/helpers';
import YoutubeURLInput from './YoutubeURLInput';
import useLazyFetch from '../../hooks/useLazyFetch';
import { useRecoilState, useSetRecoilState } from 'recoil';

interface FileSwitchProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FileSwitch = (props: FileSwitchProps) => {
	const { fileInputRef } = props;

	const [filename, setFilename] = useRecoilState(filenameSelector);
	const [fileType, setFileType] = useRecoilState(fileTypeSelector);
	const setMusicForm = useSetRecoilState(musicFormAtom);
	const setTagsLoading = useSetRecoilState(tagsLoadingSelector);

	const [getFileTags, getFileTagsStatus] = useLazyFetch<TagsResponse>();

	const onFileSwitchChange = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
			setFileType(checked ? FILE_TYPE.WAV_UPLOAD : FILE_TYPE.YOUTUBE);
		},
		[setFileType]
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
				setFilename(file.name);
				getFileTags({ url: '/music/get_tags', method: 'POST', data: formData });
			}
		},
		[getFileTags, setFilename]
	);

	useEffect(() => {
		setTagsLoading(getFileTagsStatus.isLoading);
	}, [getFileTagsStatus, setTagsLoading]);

	useEffect(() => {
		if (getFileTagsStatus.isSuccess) {
			const { title, artist, album, grouping, artwork_url } = getFileTagsStatus.data;
			setMusicForm((form) => ({
				...form,
				title: title || '',
				artist: artist || '',
				album: album || resolveAlbumFromTitle(title) || '',
				grouping: grouping || '',
				artwork_url: artwork_url || '',
			}));
		}
	}, [getFileTagsStatus.data, getFileTagsStatus.isSuccess, setMusicForm]);

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
					InputProps={{ readOnly: true }}
					disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
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
