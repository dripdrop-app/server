import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Container, Grid } from 'semantic-ui-react';
import { useDispatch, useSelector } from 'react-redux';
import { useLazyCreateFileJobQuery, useLazyCreateYoutubeJobQuery } from '../../api';
import { resetForm } from '../../state/music';
import { FILE_TYPE } from '../../utils/enums';
import BlankImage from '../../images/blank_image.jpeg';

interface FormActionProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FormActions = (props: FormActionProps) => {
	const { fileInputRef } = props;
	const [failedCreateJob, setFailedCreateJob] = useState(false);

	const [createFileJob, createFileJobStatus] = useLazyCreateFileJobQuery();
	const [createYoutubeJob, createYoutubeJobStatus] = useLazyCreateYoutubeJobQuery();

	const dispatch = useDispatch();
	const { formLoading, valid, title, artist, album, grouping, artworkUrl, fileType, youtubeUrl, validArtwork } =
		useSelector((state: RootState) => {
			let formLoading = false;
			for (const query in state.api.queries) {
				if (query.includes('grouping') || query.includes('artwork') || query.includes('tags')) {
					const call = state.api.queries[query];
					formLoading = formLoading || (call?.status === 'pending' ?? formLoading);
				}
			}
			return { formLoading, ...state.music };
		});

	const run = useCallback(async () => {
		let artwork = validArtwork ? artworkUrl : (await fetch(BlankImage)).url;
		if (
			fileType !== FILE_TYPE.YOUTUBE &&
			fileInputRef.current &&
			fileInputRef.current.files &&
			fileInputRef.current.files.length > 0
		) {
			const file = fileInputRef.current.files[0];
			createFileJob({ file, artworkUrl: artwork, title, artist, album, grouping });
		} else {
			createYoutubeJob({ youtubeUrl, artworkUrl: artwork, title, artist, album, grouping });
		}
	}, [
		album,
		artist,
		artworkUrl,
		createFileJob,
		createYoutubeJob,
		fileInputRef,
		fileType,
		grouping,
		title,
		validArtwork,
		youtubeUrl,
	]);

	useEffect(() => {
		if (!createYoutubeJobStatus.isUninitialized) {
			setFailedCreateJob(!createYoutubeJobStatus.isSuccess);
		}
		if (createYoutubeJobStatus.isSuccess) {
			dispatch(resetForm());
		}
	}, [createYoutubeJobStatus.isSuccess, createYoutubeJobStatus.isUninitialized, dispatch]);

	useEffect(() => {
		if (!createFileJobStatus.isUninitialized) {
			setFailedCreateJob(!createFileJobStatus.isSuccess);
		}
		if (createFileJobStatus.isSuccess) {
			dispatch(resetForm());
		}
	}, [dispatch, createFileJobStatus.isSuccess, createFileJobStatus.isUninitialized]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable>
					<Grid.Row>
						<Grid.Column width={4}>
							<Button
								color={failedCreateJob ? 'red' : 'blue'}
								disabled={!valid}
								onClick={run}
								loading={createFileJobStatus.isFetching || createYoutubeJobStatus.isFetching || formLoading}
							>
								{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
								{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
								{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
							</Button>
						</Grid.Column>
						<Grid.Column width={2}>
							<Button onClick={() => dispatch(resetForm())} color="blue">
								Reset
							</Button>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[
			createFileJobStatus.isFetching,
			createYoutubeJobStatus.isFetching,
			dispatch,
			failedCreateJob,
			fileType,
			formLoading,
			run,
			valid,
		]
	);
};

export default FormActions;
