import React, { useCallback, useEffect, useMemo } from 'react';
import { Grid, TextField, Switch, Button } from '@mui/material';
import { debounce } from 'lodash';
import { useSelector, useDispatch } from 'react-redux';
import { updateForm } from '../../state/music';
import { useLazyGroupingQuery, useLazyTagsQuery } from '../../api/music';
import { FILE_TYPE } from '../../utils/enums';

interface SourceSelectorProps {
	fileInputRef: React.RefObject<HTMLInputElement>;
}

const SourceSelector = (props: SourceSelectorProps) => {
	const { fileInputRef } = props;

	const [getFileTags, getFileTagsStatus] = useLazyTagsQuery();
	const [getGrouping, getGroupingStatus] = useLazyGroupingQuery();

	const dispatch = useDispatch();
	const { grouping, youtubeUrl, filename, fileType, validYoutubeLink } = useSelector((state: RootState) => ({
		youtubeUrl: state.music.youtubeUrl,
		grouping: state.music.grouping,
		filename: state.music.filename,
		fileType: state.music.fileType,
		validYoutubeLink: state.music.validYoutubeLink,
	}));

	const debouncedGetGrouping = useMemo(() => debounce(getGrouping, 1000), [getGrouping]);

	const onFileSwitchChange = useCallback(
		(event: React.FormEvent<HTMLInputElement>, checked: boolean) => {
			dispatch(updateForm({ fileType: checked ? FILE_TYPE.WAV_UPLOAD : FILE_TYPE.YOUTUBE }));
		},
		[dispatch]
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
				dispatch(updateForm({ filename: file.name }));
				const formData = new FormData();
				formData.append('file', file);
				getFileTags(file);
			}
		},
		[dispatch, getFileTags]
	);

	useEffect(() => {
		if (youtubeUrl && !grouping) {
			debouncedGetGrouping(youtubeUrl);
		}
	}, [debouncedGetGrouping, grouping, youtubeUrl]);

	useEffect(() => {
		if (getFileTagsStatus.isSuccess && getFileTagsStatus.currentData) {
			const { title, artist, album, grouping, artworkUrl } = getFileTagsStatus.currentData;
			dispatch(updateForm({ title, artist, album, grouping, artworkUrl }));
		}
	}, [dispatch, getFileTagsStatus.currentData, getFileTagsStatus.isSuccess]);

	useEffect(() => {
		if (getGroupingStatus.isSuccess && getGroupingStatus.currentData) {
			const { grouping } = getGroupingStatus.currentData;
			dispatch(updateForm({ grouping }));
		}
	}, [dispatch, getGroupingStatus.currentData, getGroupingStatus.isSuccess]);

	return useMemo(() => {
		return (
			<Grid container spacing={1} alignItems="center">
				<Grid item md={6}>
					<TextField
						fullWidth
						label="Youtube URL"
						value={youtubeUrl}
						disabled={fileType !== FILE_TYPE.YOUTUBE}
						onChange={(e) => dispatch(updateForm({ youtubeUrl: e.target.value }))}
						error={!validYoutubeLink && fileType === FILE_TYPE.YOUTUBE}
						required={fileType === FILE_TYPE.YOUTUBE}
					/>
				</Grid>
				<Grid item md={1}>
					<Switch value={fileType} checked={fileType !== FILE_TYPE.YOUTUBE} onChange={onFileSwitchChange} />
				</Grid>
				<Grid item md={5}>
					<TextField
						fullWidth
						label="Filename"
						value={filename}
						disabled
						error={filename === '' && fileType !== FILE_TYPE.YOUTUBE}
						required={fileType !== FILE_TYPE.YOUTUBE}
						onClick={onBrowseClick}
						InputProps={{
							endAdornment: (
								<Button variant="contained" disabled={fileType === FILE_TYPE.YOUTUBE}>
									Browse
								</Button>
							),
						}}
					/>
				</Grid>
				<input ref={fileInputRef} onChange={onFileChange} style={{ display: 'none' }} type="file" accept=".mp3,.wav" />
			</Grid>
		);
	}, [
		dispatch,
		fileInputRef,
		fileType,
		filename,
		onBrowseClick,
		onFileChange,
		onFileSwitchChange,
		validYoutubeLink,
		youtubeUrl,
	]);
};

export default SourceSelector;
