import { YouTube } from '@mui/icons-material';
import { TextField } from '@mui/material';
import React, { useContext, useCallback, useEffect, useMemo } from 'react';
import { MusicContext } from '../../context/Music';
import useLazyFetch from '../../hooks/useLazyFetch';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps } from '../../utils/helpers';

const YoutubeURLInput = () => {
	const { formInputs, updateFormInputs } = useContext(MusicContext);
	const { youtube_url, fileType } = formInputs;

	const [getGrouping, getGroupingStatus] = useLazyFetch();

	const validYTLink = useCallback((url: string | null) => {
		if (!url) {
			return false;
		}
		return RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(url);
	}, []);

	useEffect(() => {
		if (getGroupingStatus.isSuccess) {
			const { grouping } = getGroupingStatus.data;
			updateFormInputs({ grouping });
		}
	}, [getGroupingStatus, updateFormInputs]);

	useEffect(() => {
		if (youtube_url && validYTLink(youtube_url)) {
			const params = new URLSearchParams();
			params.append('youtube_url', youtube_url);
			getGrouping(`/music/grouping?${params}`);
		}
	}, [getGrouping, validYTLink, youtube_url]);

	return useMemo(
		() => (
			<React.Fragment>
				<YouTube
					sx={{
						color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
					}}
				/>
				<TextField
					{...defaultTextFieldProps}
					required
					value={youtube_url}
					label="YouTube URL"
					disabled={fileType !== FILE_TYPE.YOUTUBE}
					onChange={(e) => updateFormInputs({ youtube_url: e.target.value })}
					error={!validYTLink(youtube_url) && fileType === FILE_TYPE.YOUTUBE}
					helperText={youtube_url === '' ? '' : 'Must be a valid YouTube link.'}
				/>
			</React.Fragment>
		),
		[fileType, updateFormInputs, validYTLink, youtube_url]
	);
};

export default YoutubeURLInput;
