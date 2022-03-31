import React, { useCallback, useEffect, useMemo } from 'react';
import { Checkbox, CheckboxProps, Container, Grid, Input } from 'semantic-ui-react';
import { debounce } from 'lodash';
import { useSelector, useDispatch } from 'react-redux';
import { updateForm } from '../../state/music';
import { useLazyGroupingQuery, useLazyTagsQuery } from '../../api';
import { FILE_TYPE } from '../../utils/enums';

interface SourceSelectorProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
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
		(event: React.FormEvent<HTMLInputElement>, data: CheckboxProps) => {
			dispatch(updateForm({ fileType: data.checked ? FILE_TYPE.WAV_UPLOAD : FILE_TYPE.YOUTUBE }));
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
		if (getFileTagsStatus.isSuccess) {
			const { title, artist, album, grouping, artworkUrl } = getFileTagsStatus.data;
			dispatch(updateForm({ title, artist, album, grouping, artworkUrl }));
		}
	}, [dispatch, getFileTagsStatus.data, getFileTagsStatus.isSuccess]);

	useEffect(() => {
		if (getGroupingStatus.isSuccess) {
			const { grouping } = getGroupingStatus.data;
			dispatch(updateForm({ grouping }));
		}
	}, [dispatch, getGroupingStatus.data, getGroupingStatus.isSuccess]);

	return useMemo(() => {
		return (
			<Container>
				<Grid stackable>
					<Grid.Row verticalAlign="middle">
						<Grid.Column width={7}>
							<Input
								fluid
								value={youtubeUrl}
								label="Youtube URL"
								disabled={fileType !== FILE_TYPE.YOUTUBE}
								onChange={(e) => dispatch(updateForm({ youtubeUrl: e.target.value }))}
								error={!validYoutubeLink && fileType === FILE_TYPE.YOUTUBE}
								required={fileType === FILE_TYPE.YOUTUBE}
							/>
						</Grid.Column>
						<Grid.Column width={2}>
							<Checkbox
								toggle
								value={Number(fileType !== FILE_TYPE.YOUTUBE)}
								checked={fileType !== FILE_TYPE.YOUTUBE}
								onChange={onFileSwitchChange}
							/>
						</Grid.Column>
						<Grid.Column width={7}>
							<Input
								readOnly
								fluid
								action={{
									onClick: onBrowseClick,
									disabled: fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD,
									content: 'Browse',
									color: 'blue',
								}}
								value={filename}
								label="Filename"
								onChange={onFileChange}
								disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
								error={filename === '' && fileType !== FILE_TYPE.YOUTUBE}
								required={fileType !== FILE_TYPE.YOUTUBE}
							/>
						</Grid.Column>
					</Grid.Row>
				</Grid>
				<input ref={fileInputRef} onChange={onFileChange} style={{ display: 'none' }} type="file" accept=".mp3,.wav" />
			</Container>
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
