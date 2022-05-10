import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Snackbar, Stack, Alert } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useLazyCreateFileJobQuery, useLazyCreateYoutubeJobQuery } from '../../api/music';
import { resetForm } from '../../state/music';
import { FILE_TYPE } from '../../utils/enums';
import BlankImage from '../../images/blank_image.jpeg';
import ConditionalDisplay from '../ConditionalDisplay';

interface FormActionProps {
	fileInputRef: React.RefObject<HTMLInputElement>;
}

const FormActions = (props: FormActionProps) => {
	const { fileInputRef } = props;
	const [openSuccess, setOpenSuccess] = useState(false);
	const [openFailed, setOpenFailed] = useState(false);

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
		if (createYoutubeJobStatus.isSuccess) {
			setOpenSuccess(true);
			dispatch(resetForm());
		} else if (createYoutubeJobStatus.isError) {
			setOpenFailed(true);
		}
	}, [createYoutubeJobStatus.isError, createYoutubeJobStatus.isSuccess, dispatch]);

	useEffect(() => {
		if (createFileJobStatus.isSuccess) {
			setOpenSuccess(true);
			dispatch(resetForm());
		} else if (createFileJobStatus.isError) {
			setOpenFailed(true);
		}
	}, [dispatch, createFileJobStatus.isSuccess, createFileJobStatus.isError]);

	return useMemo(
		() => (
			<Stack direction="row" justifyContent="space-evenly" flexWrap="wrap">
				<Snackbar
					anchorOrigin={{ horizontal: 'center', vertical: 'top' }}
					open={openSuccess}
					autoHideDuration={5000}
					onClose={() => setOpenSuccess(false)}
				>
					<Alert onClose={() => setOpenSuccess(false)} severity="success">
						Successfully Created Job!
					</Alert>
				</Snackbar>
				<Snackbar
					anchorOrigin={{ horizontal: 'center', vertical: 'top' }}
					open={openFailed}
					autoHideDuration={5000}
					onClose={() => setOpenFailed(false)}
				>
					<Alert onClose={() => setOpenFailed(false)} severity="error">
						Failed Created Job.
					</Alert>
				</Snackbar>
				<Button
					variant="contained"
					disabled={!valid || createFileJobStatus.isFetching || createYoutubeJobStatus.isFetching || formLoading}
					onClick={run}
				>
					<ConditionalDisplay condition={fileType === FILE_TYPE.YOUTUBE}>Download and Set Tags</ConditionalDisplay>
					<ConditionalDisplay condition={fileType === FILE_TYPE.MP3_UPLOAD}>Update Tags</ConditionalDisplay>
					<ConditionalDisplay condition={fileType === FILE_TYPE.WAV_UPLOAD}>Convert and Update Tags</ConditionalDisplay>
				</Button>
				<Button variant="contained" onClick={() => dispatch(resetForm())}>
					Reset
				</Button>
			</Stack>
		),
		[
			createFileJobStatus.isFetching,
			createYoutubeJobStatus.isFetching,
			dispatch,
			fileType,
			formLoading,
			openFailed,
			openSuccess,
			run,
			valid,
		]
	);
};

export default FormActions;
