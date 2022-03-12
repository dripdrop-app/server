import React, { useCallback, useEffect, useMemo } from 'react';
import { useAtomValue } from 'jotai';
import { useResetAtom } from 'jotai/utils';
import { Button, Container, Grid } from 'semantic-ui-react';
import { FILE_TYPE } from '../../utils/enums';
import {
	artworkLoadingAtom,
	groupingLoadingAtom,
	musicFormAtom,
	tagsLoadingAtom,
	validArtworkAtom,
	validMusicForm,
} from '../../state/Music';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

interface FormActionProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FormActions = (props: FormActionProps) => {
	const { fileInputRef } = props;

	const musicForm = useAtomValue(musicFormAtom);
	const resetForm = useResetAtom(musicFormAtom);
	const validForm = useAtomValue(validMusicForm);
	const validArtwork = useAtomValue(validArtworkAtom);
	const groupingLoading = useAtomValue(groupingLoadingAtom);
	const tagsLoading = useAtomValue(tagsLoadingAtom);
	const artworkLoading = useAtomValue(artworkLoadingAtom);

	const { title, artist, album, grouping, artworkUrl, fileType, youtubeUrl } = musicForm;

	const [performOperation, performOperationStatus] = useLazyFetch();

	const run = useCallback(async () => {
		const formData = new FormData();
		if (
			fileType !== FILE_TYPE.YOUTUBE &&
			fileInputRef.current &&
			fileInputRef.current.files &&
			fileInputRef.current.files.length > 0
		) {
			const file = fileInputRef.current.files[0];
			formData.append('file', file);
		}
		if (fileType === FILE_TYPE.YOUTUBE) {
			formData.append('youtubeUrl', youtubeUrl || '');
		}
		if (validArtwork) {
			formData.append('artworkUrl', artworkUrl);
		} else {
			const imageResponse = await fetch(BlankImage);
			if (imageResponse.ok) {
				const blob = await imageResponse.blob();
				try {
					const readFilePromise: () => Promise<string | ArrayBuffer | null> = () =>
						new Promise((resolve, reject) => {
							const reader = new FileReader();
							reader.onloadend = () => resolve(reader.result);
							reader.onerror = reject;
							reader.readAsDataURL(blob);
						});
					const url = await readFilePromise();
					if (typeof url === 'string') {
						formData.append('artworkUrl', url);
					}
				} catch {}
			}
		}
		formData.append('title', title);
		formData.append('artist', artist);
		formData.append('album', album);
		formData.append('grouping', grouping || '');
		performOperation({ url: '/music/jobs/create', method: 'POST', data: formData });
	}, [album, artist, artworkUrl, fileInputRef, fileType, grouping, performOperation, title, validArtwork, youtubeUrl]);

	useEffect(() => {
		if (performOperationStatus.success) {
			resetForm();
		}
	}, [resetForm, performOperationStatus.success]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row>
						<Grid.Column width={4}>
							<Button
								color={performOperationStatus.error ? 'red' : 'blue'}
								disabled={!validForm}
								onClick={run}
								loading={performOperationStatus.loading || groupingLoading || tagsLoading || artworkLoading}
							>
								{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
								{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
								{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
							</Button>
						</Grid.Column>
						<Grid.Column width={2}>
							<Button onClick={() => resetForm()} color="blue">
								Reset
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[
			artworkLoading,
			fileType,
			groupingLoading,
			performOperationStatus.error,
			performOperationStatus.loading,
			resetForm,
			run,
			tagsLoading,
			validForm,
		]
	);
};

export default FormActions;
