import React, { useCallback, useEffect, useMemo } from 'react';
import { useAtom, useSetAtom } from 'jotai';
import { Checkbox, CheckboxProps, Container, Grid, Input } from 'semantic-ui-react';
import { filenameAtom, fileTypeAtom, musicFormAtom, tagsLoadingAtom, youtubeURLAtom } from '../../state/Music';
import { FILE_TYPE } from '../../utils/enums';
import { isValidYTLink, resolveAlbumFromTitle } from '../../utils/helpers';
import useLazyFetch from '../../hooks/useLazyFetch';

interface SourceSelectorProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const SourceSelector = (props: SourceSelectorProps) => {
	const { fileInputRef } = props;

	const [youtubeUrl, setYoutubeURL] = useAtom(youtubeURLAtom);
	const [filename, setFilename] = useAtom(filenameAtom);
	const [fileType, setFileType] = useAtom(fileTypeAtom);
	const setMusicForm = useSetAtom(musicFormAtom);
	const setTagsLoading = useSetAtom(tagsLoadingAtom);

	const validYoutubeLink = isValidYTLink(youtubeUrl);

	const [getFileTags, getFileTagsStatus] = useLazyFetch<TagsResponse>();

	const onFileSwitchChange = useCallback(
		(event: React.FormEvent<HTMLInputElement>, data: CheckboxProps) => {
			setFileType(data.checked ? FILE_TYPE.WAV_UPLOAD : FILE_TYPE.YOUTUBE);
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
				getFileTags({ url: '/music/tags', method: 'POST', data: formData });
			}
		},
		[getFileTags, setFilename]
	);

	useEffect(() => {
		setTagsLoading(getFileTagsStatus.loading);
	}, [getFileTagsStatus, setTagsLoading]);

	useEffect(() => {
		if (getFileTagsStatus.success) {
			const { title, artist, album, grouping, artworkUrl } = getFileTagsStatus.data;
			setMusicForm((form) => ({
				...form,
				title: title || '',
				artist: artist || '',
				album: album || resolveAlbumFromTitle(title),
				grouping: grouping || '',
				artworkUrl: artworkUrl || '',
			}));
		}
	}, [getFileTagsStatus.data, getFileTagsStatus.success, setMusicForm]);

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
								onChange={(e) => setYoutubeURL(e.target.value)}
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
		fileInputRef,
		fileType,
		filename,
		onBrowseClick,
		onFileChange,
		onFileSwitchChange,
		setYoutubeURL,
		validYoutubeLink,
		youtubeUrl,
	]);
};

export default SourceSelector;
