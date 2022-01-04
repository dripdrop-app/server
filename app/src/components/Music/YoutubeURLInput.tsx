import React, { useEffect } from 'react';
import { YouTube } from '@mui/icons-material';
import { TextField } from '@mui/material';
import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';
import { fileTypeSelector, groupingSelector, youtubeURLSelector } from '../../atoms/Music';
import useLazyFetch from '../../hooks/useLazyFetch';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps, isValidYTLink } from '../../utils/helpers';

const YoutubeURLInput = () => {
	const [youtubeURL, setYoutubeURL] = useRecoilState(youtubeURLSelector);
	const fileType = useRecoilValue(fileTypeSelector);

	const setGroupingSelector = useSetRecoilState(groupingSelector);

	const valid = isValidYTLink(youtubeURL);

	const [getGrouping, getGroupingStatus] = useLazyFetch<Pick<MusicForm, 'grouping'>>();

	useEffect(() => {
		if (getGroupingStatus.isSuccess) {
			const { grouping } = getGroupingStatus.data;
			if (youtubeURL) {
				setGroupingSelector(grouping);
			}
		}
	}, [getGroupingStatus, setGroupingSelector, youtubeURL]);

	useEffect(() => {
		if (youtubeURL && valid) {
			getGrouping({ url: '/music/grouping', params: { youtube_url: youtubeURL } });
		}
	}, [getGrouping, valid, youtubeURL]);

	return (
		<React.Fragment>
			<YouTube
				sx={{
					color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
				}}
			/>
			<TextField
				{...defaultTextFieldProps}
				required
				value={youtubeURL}
				label="YouTube URL"
				disabled={fileType !== FILE_TYPE.YOUTUBE}
				onChange={(e) => setYoutubeURL(e.target.value)}
				error={!valid && fileType === FILE_TYPE.YOUTUBE}
				helperText={youtubeURL ? '' : 'Must be a valid YouTube link.'}
			/>
		</React.Fragment>
	);
};

export default YoutubeURLInput;
